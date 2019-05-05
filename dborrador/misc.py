from collections import Counter, namedtuple, defaultdict

from .models import Asignacion
from materias.misc import Mapeos


Problemas = namedtuple('Problemas', ['cargas_no_distribuidas', 'necesidades_no_cubiertas', 'recargas'])

class MapeosDistribucion:

    @staticmethod
    def cargas_a_distribuir(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> {Carga}'''
        asignaciones_previas = MapeosDistribucion.asignaciones(tipo, ac, intento)
        docentes_cargas = Mapeos.docentes_y_cargas(tipo, ac)
        cargas = {c
                  for d_cargas in docentes_cargas.values()
                  for c in d_cargas}
        # TODO: chequear que no hay dos asignaciones con la misma carga
        cargas_distribuidas = {a.carga for a in asignaciones_previas}
        return cargas - cargas_distribuidas

    @staticmethod
    def necesidades_no_cubiertas(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> {Turno: necesidad}.
        Obs: necesidad puede ser < 0 (y significa una mala distribución)'''
        asignaciones_previas = MapeosDistribucion.asignaciones(tipo, ac, intento)
        asignaciones_por_turno = Counter(a.turno for a in asignaciones_previas)
        turnos = Mapeos.encuesta_tipo_turno(tipo).filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre)
        necesidades = {}
        for turno in turnos:
            necesidades[turno] = Mapeos.necesidades(turno, tipo) - asignaciones_por_turno.get(turno, 0)
        return necesidades

    @staticmethod
    def cargas_tipo_ge_a_distribuir_en(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> [Carga]'''
        todas = Mapeos.cargas_no_asignadas_en(ac)

        def union_(dicc):
            if not dicc:
                return set()
            return set.union(*(set(v) for v in dicc.values()))

        otro_tipo = union_(MapeosDistribucion.cargas_otro_tipo(ac))
        fijas = union_(MapeosDistribucion.cargas_de_asignaciones_fijas(ac))
        este_intento = union_(MapeosDistribucion.cargas_de_asignaciones_para_intento(ac, intento))

        faltan = set(todas) - otro_tipo - fijas - este_intento
        faltan_de_tipo_pedido = Mapeos.filtrar_cargas_de_tipo_ge(tipo, faltan)
        return faltan_de_tipo_pedido

    @staticmethod
    def cargas_otro_tipo(ac):
        '''Devuelve las cargas correspondientes a asignaciones con intento < 0'''
        return MapeosDistribucion._cargas_de_asignaciones_ac_filtradas(ac, lambda i: i < 0)

    @staticmethod
    def cargas_de_asignaciones_fijas(ac):
        '''Devuelve las cargas correspondientes a asignaciones con intento = 0'''
        return MapeosDistribucion._cargas_de_asignaciones_ac_filtradas(ac, lambda i: i == 0)

    @staticmethod
    def cargas_de_asignaciones_para_intento(ac, intento):
        '''Devuelve las cargas correspondientes a asignaciones con intento = intento'''
        return MapeosDistribucion._cargas_de_asignaciones_ac_filtradas(ac, lambda i: i == intento)

    @staticmethod
    def asignaciones_para_todos_los_intentos(ac):
        '''Devuelve las asignaciones con intento >= 0. No las de intento < 0'''
        return Asignacion.objects.filter(turno__anno=ac.anno,
                                         turno__cuatrimestre=ac.cuatrimestre,
                                         intento__gte=0)

    @staticmethod
    def _cargas_de_asignaciones_ac_filtradas(ac, filtro_intento):
        '''{Turno -> [Carga]}'''
        ret = defaultdict(list)
        asignaciones = Asignacion.objects.filter(turno__anno=ac.anno,
                                                 turno__cuatrimestre=ac.cuatrimestre)
        for a in asignaciones:
            if filtro_intento(a.intento):
                ret[a.turno].append(a.carga)

        return ret

    @staticmethod
    def necesidades_tipo_no_cubiertas_en(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> {Turno -> Int}
        Este método asume que las cargas ya publicadas (en materias.Carga con turno asignado)
        y las asignaciones con intento < 0 no corresponden a lo que se está distribuyendo.
        Por eso no se descuentan de las necesidades.
        Y las asignaciones con intento >= 0 sí corresponden a lo que se está distribuyendo.

        TODO: verificar que la distribución que se está haciendo nunca se va a mezclar
        con distribuciones de otros TipoDocentes ni con lo que ya está publicado.
        Si hay alguna posibilidad de que sí se mezcle, se puede
        * agregar a cada carga y/o asignación que TipoDocentes está cubriendo
        * tocar las necesidades a mano (esto es feo porque puede romper cuatrimestres que siguen
            si se copian las necesidades de un año a otro).
        '''
        def cantidad(turno_cargas):
            return Counter(turno for turno, cargas in turno_cargas.items()
                           for _ in cargas)

        fijas = cantidad(MapeosDistribucion.cargas_de_asignaciones_fijas(ac))
        para_intento = cantidad(MapeosDistribucion.cargas_de_asignaciones_para_intento(ac, intento))
        necesidades = Counter(Mapeos.turno_y_necesidad(tipo, ac))
        # TODO: qué se hace si en algún turno necesidades < fijas + para_intento ?
        #       Ahora no se hace nada (la cuenta da 0 y listo)
        return necesidades - (fijas + para_intento)

    @staticmethod
    def asignaciones(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> [Asignacion]'''
        cargas = Mapeos.cargas(tipo, ac)
        asignaciones = Asignacion.objects.filter(turno__anno=ac.anno,
                                                 turno__cuatrimestre=ac.cuatrimestre,
                                                 intento=intento)
        return [a for a in asignaciones if a.carga in cargas]

    @staticmethod
    def docentes_y_asignaciones(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> {Docente: [Asignacion]}'''
        cargas = Mapeos.cargas(tipo, ac)
        # TODO: agregar intento 0
        asignaciones = Asignacion.objects.filter(turno__anno=ac.anno,
                                                 turno__cuatrimestre=ac.cuatrimestre,
                                                 intento=intento)
        ret = defaultdict(list)
        for asignacion in asignaciones:
            if asignacion.carga in cargas:
                ret[asignacion.carga.docente].append(asignacion)
        return ret

    @staticmethod
    def chequeo(tipo, ac, intento, este_tipo_fijo, este_tipo):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> ([Carga], [Turno, necesidad])'''
        cargas = MapeosDistribucion.cargas_tipo_ge_a_distribuir_en(tipo, ac, intento)
        necesidades = MapeosDistribucion.necesidades_tipo_no_cubiertas_en(tipo, ac, intento)
        no_cubiertas = [(turno, necesidad) for turno, necesidad in necesidades.items() if necesidad > 0]
        recargas = MapeosDistribucion.docentes_recargados(este_tipo_fijo, este_tipo, intento)
        return Problemas(cargas, no_cubiertas, recargas)

    @staticmethod
    def docentes_recargados(fijas, para_intento, intento):
        '''{Turno: [Carga]} -> {Turno: [Carga]} -> intento -> {Carga: [Asignacion]}'''
        cantidades_fijas = Counter([carga for lista_cargas in fijas.values()
                                          for carga in lista_cargas])
        cantidades_para_intento = Counter([carga for lista_cargas in para_intento.values()
                                                 for carga in lista_cargas])
        totales = cantidades_fijas + cantidades_para_intento
        recargas = [carga for carga, cantidad in totales.items() if cantidad > 1]

        ret = dict()
        for carga in recargas:
            ret[carga] = list(Asignacion.objects.filter(carga=carga, intento=0)) \
                         + list(Asignacion.objects.filter(carga=carga, intento=intento))

        return ret