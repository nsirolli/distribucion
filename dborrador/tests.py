from django.test import TestCase, Client
from django.utils import timezone

import re

from dborrador.models import Preferencia, Asignacion
from materias.models import Docente, Materia, Turno, Cuatrimestres, Cargos, TipoTurno, TipoMateria
from encuestas.models import PreferenciasDocente

class TestPreparar(TestCase):

    def test_no_falla_si_no_hay_preferencias(self):
        c = Client()
        response = c.get('/dborrador/preparar')
        self.assertEqual(response.status_code, 200)

        response = c.post('/dborrador/preparar', {'anno': '2100', 'cuatrimestre': 'P', 'tipo': 'P'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertTrue(re.search('Copiadas:[^0-9]*0[^0-9]*\n', content),
                        'La página deberia decir que se copiaron 0 preferencias')
        self.assertTrue(re.search('Borradas:[^0-9]*0[^0-9]*\n', content),
                        'La página deberia decir que se borraron 0 preferencias')
        self.assertTrue('Preferencias copiadas' in response.content.decode(),
                        'La página debería decir "Preferencias copiadas" y dice {}'.format(
                            response.content.decode()))

    def test_copia_preferencias(self):
        docente = Docente.objects.create(nombre='juan', email='mail@nada.org',
                                         telefono='1234', cargo=Cargos.Tit.name)
        materia = Materia.objects.create(nombre='epistemologia', obligatoriedad=TipoMateria.B.name)
        turno1 = Turno.objects.create(materia=materia, anno=2100, cuatrimestre=Cuatrimestres.P.name,
                                      numero=1, tipo=TipoTurno.A.name,
                                      necesidad_prof=1, necesidad_jtp=0, necesidad_ay1=0, necesidad_ay2=0)
        turno2 = Turno.objects.create(materia=materia, anno=2100, cuatrimestre=Cuatrimestres.P.name,
                                      numero=2, tipo=TipoTurno.A.name,
                                      necesidad_prof=1, necesidad_jtp=0, necesidad_ay1=0, necesidad_ay2=0)
        now = timezone.now()
        pref1 = PreferenciasDocente.objects.create(docente=docente, turno=turno1, peso=1, fecha_encuesta=now)
        pref2 = PreferenciasDocente.objects.create(docente=docente, turno=turno2, peso=3, fecha_encuesta=now)

        c = Client()
        response = c.post('/dborrador/preparar', {'anno': '2100', 'cuatrimestre': 'P', 'tipo': 'P'})
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('Copiadas:[^0-9]*2[^0-9]*\n', content),
                        'La página deberia decir que se copiaron 2 preferencias')
        self.assertTrue(re.search('Borradas:[^0-9]*0[^0-9]*\n', content),
                        'La página deberia decir que se borraron 0 preferencias')
        self.assertEqual(Preferencia.objects.all().count(), 2, 'Debería haber dos preferencias copiadas')


class TestPaginaPrincipal(TestCase):

    def test_hay_pagina_principal(self):
        c = Client()
        response = c.get('/dborrador/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('<a href=.preparar.>', response.content.decode()),
                        'La página principal no contiene un link a /dborrador/preparar')
        self.assertTrue(re.search('<a href=.distribuir.>', response.content.decode()),
                        'La página principal no contiene un link a /dborrador/distribuir')
        self.assertTrue(re.search('<a href=.distribucion/\d+/[PSV]/[PJA12]/\d+', response.content.decode()),
                        'La página principal no contiene un link a /dborrador/distribucion/... completo')