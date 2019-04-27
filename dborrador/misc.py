from collections import Counter, namedtuple, defaultdict

from .models import Asignacion
from materias.misc import Mapeos


Problemas = namedtuple('Problemas', ['cargas_no_distribuidas', 'necesidades_no_cubiertas'])

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

        otro_tipo = union_(MapeosDistribucion.asignaciones_otro_tipo(ac))
        fijas = union_(MapeosDistribucion.asignaciones_fijas(ac))
        este_intento = union_(MapeosDistribucion.asignaciones_para_intento(ac, intento))

        faltan = set(todas) - otro_tipo - fijas - este_intento
        faltan_de_tipo_pedido = Mapeos.filtrar_cargas_de_tipo_ge(tipo, faltan)
        return faltan_de_tipo_pedido

    # TODO:
    ## 1. cargas con turno asignado  // Mapeos.cargas_asignadas_en : AnnoCuatrimestre -> {Turno -> [Carga]}

    ## 2. cargas sin turno asignado // Mapeos.cargas_no_asignadas_en : AnnoCuatrimestre -> [Carga]

    ## 3. asignaciones con intento < 0 (en Asignacion)
    #           // MapeosDistribucion.asignaciones_otro_tipo : AnnoCuatrimestre -> {Turno -> [Carga]}
    ## 4. asignaciones con intento = 0
    #           // MapeosDistribucion.asignaciones_fijas : AnnoCuatrimestre -> {Turno -> [Carga]}
    ## 5. asignaciones con intento = intento
    #           // MapeosDistribucion.asignaciones_para_intento : AnnoCuatrimestre -> intento -> {Turno -> [Carga]}

    ## 6. filtrar cargas por cargo >= tipo
    #           // Mapeos.filtrar_cargas_de_tipo_ge(tipo, [Carga]) : [Carga]

    ## 7. necesidades
    #           // Mapeos.turno_y_necesidad : Tipo -> AnnoCuatrimestre -> {Turno -> Int}
    ## 8. necesidades no cubiertas = 7. - (4. + 5.)
    #           // MapeosDistribucion.necesidades_tipo_no_cubiertas_en : Tipo -> AnnoCuatrimestre -> intento -> {Turno -> Int}
    ## 9. cargas a distribuir = 6.2. - 6.(3. + 4. + 5.)
    #           // MapeosDistribucion.cargas_tipo_ge_a_distribuir_en : Tipo -> AnnoCuatrimestre -> intento -> [Carga]

    # ver distribucion
    #   { otro_tipo: cargas y asignaciones otro tipo (1. + 3.)
    #     este_tipo_fijo: cargas con intento = 0 (4.)
    #     este_tipo: cargas con intento = intento (5.)
    #   }
    #
    # fijar:
    #   { mismo dict que para distribución }
    #   necesidades no cubiertas
    #   cargas a distribuir (9.) (para armar las listas)

    @staticmethod
    def asignaciones_otro_tipo(ac):
        '''Devuelve las asignaciones con intento < 0'''
        return MapeosDistribucion._asignaciones_ac_filtradas(ac, lambda i: i < 0)

    @staticmethod
    def asignaciones_fijas(ac):
        '''Devuelve las asignaciones con intento = 0'''
        return MapeosDistribucion._asignaciones_ac_filtradas(ac, lambda i: i == 0)

    @staticmethod
    def asignaciones_para_intento(ac, intento):
        '''Devuelve las asignaciones con intento = intento'''
        return MapeosDistribucion._asignaciones_ac_filtradas(ac, lambda i: i == intento)

    @staticmethod
    def _asignaciones_ac_filtradas(ac, filtro_intento):
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

        fijas = cantidad(MapeosDistribucion.asignaciones_fijas(ac))
        para_intento = cantidad(MapeosDistribucion.asignaciones_para_intento(ac, intento))
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
    def chequeo(tipo, ac, intento):
        '''TipoDocentes -> AnnoCuatrimestre -> intento -> ([Carga], [Turno, necesidad])'''
        cargas = MapeosDistribucion.cargas_a_distribuir(tipo, ac, intento)
        necesidades = MapeosDistribucion.necesidades_no_cubiertas(tipo, ac, intento)
        no_cubiertas = [(turno, necesidad) for turno, necesidad in necesidades.items() if necesidad > 0]
        return Problemas(cargas, no_cubiertas)
