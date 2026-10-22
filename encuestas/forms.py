from django.forms import ModelForm, widgets, DateTimeField, DateTimeInput
from functools import partial

from .models import EncuestasHabilitadas

DateTimeInput = partial(widgets.DateTimeInput, {'class': 'datepicker'}, format=("%d/%m/%Y %H:%M"))

FORMATOS_FECHA = ['%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y']


class HabilitacionDeEncuestaForm(ModelForm):

    desde = DateTimeField(
        widget=DateTimeInput(format='%d/%m/%Y %H:%M', attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        input_formats=FORMATOS_FECHA,
    )
    hasta = DateTimeField(
        widget=DateTimeInput(format='%d/%m/%Y %H:%M', attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        input_formats=FORMATOS_FECHA,
    )

    class Meta:
        model = EncuestasHabilitadas
        fields = '__all__'
        labels = {
            'anno': 'Año',
        }
        widgets = {
            'anno': widgets.NumberInput(attrs={'max': 2100, 'min': 2010, 'class': 'anno'})
        }
