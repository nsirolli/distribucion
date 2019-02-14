from collections import namedtuple

from django.db import models
from django.core.validators import int_list_validator, validate_comma_separated_integer_list
from enum import Enum


class Dias(Enum):
    Lu = 'Lunes'
    Ma = 'Martes'
    Mi = 'Miércoles'
    Ju = 'Jueves'
    Vi = 'Viernes'


class Cargos(Enum):
    Tit = 'Prof. Titular'
    Aso = 'Prof. Asociado'
    Adj = 'Prof. Adjunto'
    JTP = 'Jefe de Trabajos Prácticos'
    Ay1 = 'Ayudante de 1ra'
    Ay2 = 'Ayudante de 2da'


class TurnoTipos(Enum):
    T = 'Teórica'
    P = 'Práctica'
    A = 'Teórico-Práctica'


class Cuatrimestres(Enum):
    P = '1'
    S = '2'
    V = 'V'


class TipoMateria(Enum):
    B = 'obligatoria'
    R = 'optativa regular'
    N = 'optativa no regular'


def choice_enum(enum_cls):
    return ((e.name, e.value) for e in enum_cls)


TurnoInfo = namedtuple('TurnoInfo', ['tipoynumero', 'diayhora', 'aula', 'pabellon'])


class Mapeos:
    '''Esta clase resuelve distintos tipos de mapeos'''

    @staticmethod
    def docentes(tipo):
        '''P: profesor, J: JTP y Ay1, A: Ay2'''
        el_mapa = {'P': [Cargos.Tit.name, Cargos.Aso.name, Cargos.Adj.name],
                   'J': [Cargos.JTP.name, Cargos.Ay1.name],
                   'A': [Cargos.Ay2.name],
                   }
        cargos = el_mapa[tipo.upper()]
        return Docente.objects.filter(cargo__in=cargos)

    @staticmethod
    def encuesta_tipo_turno(tipo_docente):
        '''
        Para profesores: teóricas y teórico-prácticas.
        Para auxiliares: prácticas y teórico-prácticas.
        '''
        el_mapa = {'P': [TurnoTipos.T.name, TurnoTipos.A.name],
                   'J': [TurnoTipos.P.name, TurnoTipos.A.name],
                   'A': [TurnoTipos.P.name, TurnoTipos.A.name],
                   }
        tipos = el_mapa[tipo_docente.upper()]
        return Turno.objects.filter(tipo__in=tipos)



class Materia(models.Model):
    nombre = models.CharField(max_length=80)
    obligatoriedad = models.CharField(max_length=1, choices=choice_enum(TipoMateria))

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    anno = models.IntegerField()
    cuatrimestre = models.CharField(max_length=1, choices=choice_enum(Cuatrimestres))
    numero = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=choice_enum(TurnoTipos))
    necesidades = models.CharField(max_length=5, validators=[validate_comma_separated_integer_list])

    def __str__(self):
        return f'{self.materia.nombre}: {self.tipo} {self.numero}'

    def horarios_info(self):

        def time_str(hms):
            if hms.minute:
                return f'{hms.hour}:{hms.minute:02d}'
            return f'{hms.hour}'

        def join(lst):
            if len(set(lst)) == 1:
                return lst[0]
            return ' y '.join(lst)

        tipoynumero = f'{TurnoTipos[self.tipo].value} {self.numero}'
        horarios = self.horario_set.all()
        dias = join([h.dia for h in horarios])
        horas = join([f'{time_str(h.comienzo)} a {time_str(h.final)}' for h in horarios])
        aulas = join([f'{h.aula}' for h in horarios])
        pabellones = join([f'{h.pabellon}' for h in horarios])
        return TurnoInfo(tipoynumero, f'{dias}: {horas}', aulas, pabellones)

    def docentes(self):
        return ' - '.join([f'{carga.docente.nombre}' for carga in self.carga_set.all()])


class Horario(models.Model):
    dia = models.CharField(max_length=2, choices=choice_enum(Dias))
    comienzo = models.TimeField('comienzo')
    final = models.TimeField('final')
    aula = models.IntegerField(blank=True, null=True)
    pabellon = models.IntegerField(blank=True, null=True)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.turno}: {self.dia}  {self.comienzo}--{self.final}'


class Docente(models.Model):
    nombre = models.CharField(max_length=60)
    telefono = models.CharField(max_length=15, validators=[int_list_validator(sep=' ')])
    email = models.EmailField()
    cargo = models.CharField(max_length=3, choices=choice_enum(Cargos))
    cargas = models.IntegerField()

    def __str__(self):
        return f'{self.nombre}'


class Carga(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=3, choices=choice_enum(Cargos))
    turno = models.ForeignKey(Turno, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'carga docente'
        verbose_name_plural = 'cargas docentes'

    def __str__(self):
        return f'{self.docente} -> {self.turno}'
