from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MaxValueValidator
from django.utils import timezone
from enum import Enum
from datetime import datetime

from materias.models import Turno, Docente, Cuatrimestres, Cargos, TipoDocentes, choice_enum, telefono_validator

class GrupoCuatrimestral(Enum):
    V = 'Verano'
    P = '1'
    S = '2'
    VP = 'V. y 1'
    VPS = 'todos'


class PreferenciasDocente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    tipo_docente = models.CharField(max_length=2, choices=choice_enum(TipoDocentes))
    peso = models.FloatField(null=True)
    fecha_encuesta = models.DateTimeField()
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.docente} -- {self.peso} -> {self.turno}'


class OtrosDatos(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    fecha_encuesta = models.DateTimeField()
    anno = models.IntegerField()
    cuatrimestre = models.CharField(max_length=3, choices=choice_enum(GrupoCuatrimestral))  # TODO: deberia ser cuatrimestres
    comentario = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(validators=[telefono_validator], max_length=17, blank=True)
    cargas_declaradas = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=0)
    tipo_docente = models.CharField(max_length=2, choices=choice_enum(TipoDocentes))

    class Meta:
        ordering = ['fecha_encuesta']


class CargasPedidas(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    anno = models.IntegerField()
    cuatrimestre = models.CharField(max_length=1, choices=choice_enum(Cuatrimestres))
    cargas = models.PositiveIntegerField(validators=[MaxValueValidator(3)])
    tipo_docente = models.CharField(max_length=2, choices=choice_enum(TipoDocentes))
    fecha_encuesta = models.DateTimeField()


class EncuestasHabilitadas(models.Model):
    mes = datetime.today().month
    anno_def = datetime.today().year
    if mes > 8:
        anno_def += 1
    anno = models.IntegerField(default = anno_def)
    cuatrimestres = models.CharField(max_length=3, choices=choice_enum(GrupoCuatrimestral))
    minimo_de_opciones = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=5)
    minimo_de_opciones_simple = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=3)
    maximo_de_opciones = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=6)
    opciones_dificiles = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=2)
    minimo_de_opciones_verano = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=2)
    maximo_de_opciones_verano = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=3)
    opciones_dificiles_verano = models.PositiveIntegerField(validators=[MaxValueValidator(6)], default=2)
    tipo_docente = models.CharField(max_length=2, choices=choice_enum(TipoDocentes))
    desde = models.DateTimeField()
    hasta = models.DateTimeField()

    class Meta:
        unique_together = [['anno', 'cuatrimestres', 'tipo_docente']]
        ordering = ['anno', 'tipo_docente']

    def cuatrimestres_str(self):
        return '|'.join(Cuatrimestres[c].value for c in self.cuatrimestres)

    def tipo_str(self):
        return TipoDocentes[self.tipo_docente].value if self.tipo_docente else ''

    def es_valida_ahora(self, momento=None):
        if momento is None:
            momento = timezone.now()
        return self.desde <= momento <= self.hasta

    def opciones(self):
        res = (
            {
                'tmin':self.minimo_de_opciones,\
                'tminS':self.minimo_de_opciones_simple,\
                'tmax':self.maximo_de_opciones,\
                'tdif':self.opciones_dificiles\
            },
            {
                'tmin':self.minimo_de_opciones_verano,\
                'tminS':self.minimo_de_opciones_verano,\
                'tmax':self.maximo_de_opciones_verano,\
                'tdif':self.opciones_dificiles_verano\
            }
               )
        return res


    @staticmethod
    def esta_habilitada(anno, cuatrimestres, tipo_docente, momento):
        try:
            habilitacion = EncuestasHabilitadas.objects.get(anno=anno, cuatrimestres=cuatrimestres, tipo_docente=tipo_docente)
            return habilitacion.es_valida_ahora(momento)
        except EncuestasHabilitadas.DoesNotExist:
            return False
