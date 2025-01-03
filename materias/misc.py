from enum import Enum
from collections import namedtuple, defaultdict

from materias.models import Docente, Turno, Carga, TipoTurno, Cargos, CargoDedicacion, TipoDocentes, AnnoCuatrimestre


class NoTurno:
    def __init__(self, _id=-1, **kwargs):
        self.__dict__.update(kwargs)
        self.id = _id

    def __str__(self):
        return '_____ ningún turno _____'


class Mapeos:
    '''Esta clase resuelve distintos tipos de mapeos'''

    tipo_a_cargos = {TipoDocentes.P: [Cargos.Tit, Cargos.Aso, Cargos.Adj, Cargos.Vis, Cargos.Eme, Cargos.Hon, Cargos.Con, Cargos.Ple,],
                     TipoDocentes.J: [Cargos.JTP],
                     TipoDocentes.A1: [Cargos.Ay1],
                     TipoDocentes.A2: [Cargos.Ay2],
                     TipoDocentes.BI: [Cargos.Bec],
                     }

    cargos_a_tipo = {
        Cargos.Tit: TipoDocentes.P,
        Cargos.Aso: TipoDocentes.P,
        Cargos.Adj: TipoDocentes.P,
        Cargos.Eme: TipoDocentes.P,
        Cargos.Hon: TipoDocentes.P,
        Cargos.Con: TipoDocentes.P,
        Cargos.Ple: TipoDocentes.P,
        Cargos.Vis: TipoDocentes.P,
        Cargos.JTP: TipoDocentes.J,
        Cargos.Ay1: TipoDocentes.A1,
        Cargos.Ay2: TipoDocentes.A2,
        # Cargos.Bec: TipoDocentes.BI,
    }

    @staticmethod
    def cargas_de_tipo(cargas, tipo):
        '''[Carga] -> TipoDocentes -> [Carga]'''
        return [carga for carga in cargas if Cargos[carga.cargo[:3]] in Mapeos.tipo_a_cargos[tipo]]

    @staticmethod
    def cargos_de_tipos(tipo):
        '''TipoDocentes -> [CargoDedicacion]'''
        cardeds = [cd
                   for cargo in Mapeos.tipo_a_cargos[tipo]
                   for cd in CargoDedicacion.con_cargo(cargo)]
        return cardeds

    @staticmethod
    def tipo_de_carga(carga):
        '''Carga -> TipoDocentes'''
        return Mapeos.cargos_a_tipo[Cargos[carga.cargo[:3]]]

    @staticmethod
    def key_orden_por_tipo_docente(carga):
        return (Mapeos.tipo_de_carga(carga), carga.docente.na_apellido, carga.docente.na_nombre)


    @staticmethod
    def tipos_de_cargo(cargodedicacion):
        '''CargoDedicacion -> TipoDocentes'''
        el_mapa = {Cargos.Tit.name: TipoDocentes.P,
                   Cargos.Aso.name: TipoDocentes.P,
                   Cargos.Adj.name: TipoDocentes.P,
                   Cargos.Eme.name: TipoDocentes.P,
                   Cargos.Hon.name: TipoDocentes.P,
                   Cargos.Con.name: TipoDocentes.P,
                   Cargos.Ple.name: TipoDocentes.P,
                   Cargos.Vis.name: TipoDocentes.P,
                   Cargos.JTP.name: TipoDocentes.J,
                   Cargos.Ay1.name: TipoDocentes.A1,
                   Cargos.Ay2.name: TipoDocentes.A2,
                   Cargos.Bec.name: TipoDocentes.BI
                   }
        return el_mapa[cargodedicacion[:3]]

    @staticmethod
    def docentes_de_tipo(tipo, anno, cuatrimestres='VPS'):
        '''TipoDocentes -> anno -> [docente]'''
        cardeds = Mapeos.cargos_de_tipos(tipo)
        return {carga.docente for carga in Carga.objects.filter(cargo__in=cardeds, anno=anno, cuatrimestre__in=cuatrimestres)}

    @staticmethod
    def docentes_y_cargas(tipo, ac):
        '''TipoDocentes -> AnnoCuatrimestre -> {docente: [carga]}'''
        cargos = Mapeos.cargos_de_tipos(tipo)
        ret = defaultdict(list)
        for carga in Carga.objects.filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre, cargo__in=cargos):
            ret[carga.docente].append(carga)
        return ret

    @staticmethod
    def docentes_con_cargo_de_tipo(tipo):
        '''TipoDocentes -> [docente]
        Es similar a docentes_de_tipo pero mira el cargo del docente y no el cargo de la carga :-/
        '''
        cardeds = Mapeos.cargos_de_tipos(tipo)
        return Docente.objects.filter(cargos__overlap=cardeds).all()

    @staticmethod
    def becarios():
        cardeds = ['Bec']
        return Docente.objects.filter(cargos__overlap=cardeds).all()

    @staticmethod
    def turnos_de_tipo_y_ac(tipo, ac):
        '''TipoDocentes -> AnnoCuatrimestre -> [Turno]'''
        return Mapeos.encuesta_tipo_turno(tipo).filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre)

    @staticmethod
    def turno_y_necesidad(tipo, ac):
        '''TipoDocentes -> AnnoCuatrimestre -> {turno: necesidad}'''
        return {turno: Mapeos.necesidades(turno, tipo)
                for turno in Mapeos.turnos_de_tipo_y_ac(tipo, ac)}

    @staticmethod
    def necesidades_por_turno_y_tipo(ac):
        '''AnnoCuatrimestre -> {Turno -> TipoDocentes -> int}'''
        return {turno: {tipo: Mapeos.necesidades(turno, tipo)
                        for tipo in TipoDocentes}
                for turno in Turno.objects.filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre)}

    @staticmethod
    def encuesta_tipo_turno(tipo_docente):
        '''
        Para profesores: teóricas y teórico-prácticas.
        Para auxiliares: prácticas y teórico-prácticas.
        '''
        el_mapa = {TipoDocentes.P: [TipoTurno.T.name, TipoTurno.A.name],
                   TipoDocentes.J: [TipoTurno.P.name, TipoTurno.A.name, TipoTurno.L.name],
                   TipoDocentes.A1: [TipoTurno.P.name, TipoTurno.A.name, TipoTurno.L.name],
                   TipoDocentes.A2: [TipoTurno.P.name, TipoTurno.A.name, TipoTurno.L.name],
                   }
        tipos = el_mapa[tipo_docente]
        return Turno.objects.filter(tipo__in=tipos)

    @staticmethod
    def cargas(tipo, ac):
        '''TipoDocentes -> AnnoCuatrimestre -> {Carga}'''
        doc_y_cargas = Mapeos.docentes_y_cargas(tipo, ac)
        return {c for d_cargas in doc_y_cargas.values() for c in d_cargas}

    @staticmethod
    def cargas_no_asignadas_en(ac):
        '''AnnoCuatrimestre -> [Carga]'''
        return [carga
                for carga in Carga.objects.filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre)
                if carga.turno is None]

    @staticmethod
    def cargas_asignadas_en(ac):
        '''AnnoCuatrimestre -> {Turno: [Carga]}'''
        ret = defaultdict(list)
        for carga in Carga.objects.filter(anno=ac.anno, cuatrimestre=ac.cuatrimestre, turno__isnull=False):
            ret[carga.turno].append(carga)
        return ret

    @staticmethod
    def necesidades(turno, tipo_docente):
        if tipo_docente == TipoDocentes.P:
            return turno.necesidad_prof
        elif tipo_docente == TipoDocentes.J:
            return turno.necesidad_jtp
        elif tipo_docente == TipoDocentes.A1:
            return turno.necesidad_ay1
        else:
            return turno.necesidad_ay2

    @staticmethod
    def necesidades_no_cubiertas(turno, tipo_docente):
        ''' Turno -> TipoDocentes -> int ( = turno.necesidades - #{cargas de tipo_docente} )'''
        cubiertas = len([c for c in turno.carga_set.all() if Mapeos.tipo_de_carga(c) == tipo_docente])
        return Mapeos.necesidades(turno, tipo_docente) - cubiertas

    @staticmethod
    def filtrar_cargas_de_tipo_le(tipo_docente, cargas):
        '''TipoDocentes -> [Carga] -> [Carga]'''
        return [carga
                for carga in cargas
                if Mapeos.tipos_de_cargo(carga.cargo) <= tipo_docente
                ]
