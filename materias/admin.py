from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db import models
from django.forms.widgets import TimeInput, Select

from .models import Materia, Turno, Horario, Docente, Carga



class HorariosInLine(admin.TabularInline):

    model = Horario
    max_num = 3
    formfield_overrides = {
        models.TimeField: {'widget': Select(choices=(('', ''),
                                                     *((f'{hora:02d}:{minutos:02d}:00', f'{hora:02d}:{minutos:02d}')
                                                       for hora in range(6, 24) for minutos in (0, 30) )
                                                     ))},
    }


class TurnoAdmin(admin.ModelAdmin):

    inlines = [HorariosInLine]


admin.site.register([Materia, Carga, Docente], SimpleHistoryAdmin)
admin.site.register([Turno], TurnoAdmin)
