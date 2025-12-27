import ipdb
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.forms import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.validators import EmailValidator
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.conf import settings

from materias.models import Turno, Docente, Cargos, CargoDedicacion, TipoTurno, Cuatrimestres, TipoDocentes, AnnoCuatrimestre, Carga
from materias.misc import Mapeos
from encuestas.models import (PreferenciasDocente, OtrosDatos, CargasPedidas,
                              EncuestasHabilitadas, GrupoCuatrimestral, telefono_validator)
from encuestas.forms import HabilitacionDeEncuestaForm

from locale import strxfrm
from collections import Counter, namedtuple
from enum import Enum
import logging
import logging.config
logger = logging.getLogger(__name__)

#login
from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from materias.models import Carga #TODO llevar arriba
from .models import CodigoVerificacion #TODO llevar arriba

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        # Paso 1: Validar que el email pertenece a un docente
        try:
            docente = Docente.objects.get(email=email)
            
            # Generar y enviar código
            codigo_obj = CodigoVerificacion.generar_codigo(email)
            
            # Enviar email con el código
            subject = 'Tu código de verificación'
            message = f'''
            Hola {docente.nombre if hasattr(docente, 'nombre') else 'Docente'},
            
            Tu código de verificación es: {codigo_obj.codigo}
            
            Este código es válido por 10 minutos.
            
            Si no solicitaste este código, ignora este mensaje.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            # Guardar email en sesión para el próximo paso
            request.session['email_verificacion'] = email
            request.session['codigo_id'] = codigo_obj.id
            
            messages.success(request, 'Se ha enviado un código de verificación a tu correo.')
            return redirect('encuestas:verificar_codigo')
            
        except Docente.DoesNotExist:
            messages.error(request, 'No existe un docente registrado con este correo.')
        except Exception as e:
            messages.error(request, f'Error al enviar el código: {str(e)}')
    
    return render(request, 'login/email_login.html')

@csrf_protect
def verificar_codigo_view(request):
    email = request.session.get('email_verificacion')
    
    if not email:
        messages.error(request, 'Por favor, ingresa tu email primero.')
        return redirect('encuestas:login')
    
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()
        
        try:
            codigo_obj = CodigoVerificacion.objects.filter(
                email=email
            ).order_by('-creado').first()
            
            if not codigo_obj:
                messages.error(request, 'No se encontró un código de verificación. Solicita uno nuevo.')
                return redirect('encuestas:login')
            
            if not codigo_obj.es_valido():
                messages.error(request, 'El código ha expirado o es inválido. Solicita uno nuevo.')
                codigo_obj.delete()
                return redirect('encuestas:login')
            
            if codigo_obj.codigo == codigo_ingresado:
                # Código correcto, autenticar al docente
                try:
                    docente = Docente.objects.get(email=email)
                    
                    # Guardar datos del docente en sesión
                    request.session['docente_id'] = docente.id
                    request.session['docente_email'] = docente.email
                    request.session['docente_nombre'] = getattr(docente, 'nombre', '')
                    
                    # Marcar código como usado
                    codigo_obj.marcar_usado()
                    
                    # Limpiar sesión temporal
                    if 'email_verificacion' in request.session:
                        del request.session['email_verificacion']
                    
                    messages.success(request, f'¡Bienvenido {getattr(docente, "nombre", "Docente")}!')
                    
                    # ⭐ CAMBIO AQUÍ: Redirigir a la vista de encuesta en lugar de dashboard
                    # Obtener los parámetros actuales o usar unos por defecto
                    # Puedes ajustar estos valores según tu lógica
                    # FIXME
                    # anno_actual = datetime.now().year
                    anno_actual = 2026
                    cuatrimestre_actual = 'P'  # o la lógica que uses
                    tipo_docente = 'P'  # o el tipo que corresponda
                    
                    return redirect('encuestas:encuesta', 
                                   anno=anno_actual,
                                   cuatrimestres=cuatrimestre_actual,
                                   tipo_docente=tipo_docente)
                    
                except Docente.DoesNotExist:
                    messages.error(request, 'Error al autenticar. Contacta al administrador.')
            else:
                # Código incorrecto
                codigo_obj.incrementar_intentos()
                intentos_restantes = 3 - codigo_obj.intentos
                
                if intentos_restantes > 0:
                    messages.error(request, f'Código incorrecto. Te quedan {intentos_restantes} intentos.')
                else:
                    messages.error(request, 'Demasiados intentos fallidos. Solicita un nuevo código.')
                    codigo_obj.delete()
                    return redirect('encuestas:login')
                
        except CodigoVerificacion.DoesNotExist:
            messages.error(request, 'Código no válido. Solicita uno nuevo.')
            return redirect('encuestas:login')
    
    return render(request, 'login/verificar_codigo.html', {'email': email})

def logout_view(request):
    auth_logout(request)
    request.session.flush()  # Limpiar toda la sesión
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('encuestas:login')

def docente_autenticado_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificar que el docente está autenticado
        if 'docente_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('encuestas:login')
        
        # Verificar que el docente existe
        try:
            docente_id = request.session['docente_id']
            docente = Docente.objects.get(id=docente_id)
            # Pasar el docente al contexto de la vista
            kwargs['docente_autenticado'] = docente
        except Docente.DoesNotExist:
            messages.error(request, 'Tu sesión no es válida. Por favor, inicia sesión nuevamente.')
            # Limpiar sesión inválida
            if 'docente_id' in request.session:
                del request.session['docente_id']
            return redirect('encuestas:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
#login


@login_required
@permission_required('dborrador.add_asignacion')
def index(request):
    return render(request, 'encuestas/administrar.html')


@login_required
@permission_required('dborrador.add_asignacion')
def administrar_habilitadas(request):
    context = {
        'habilitadas': EncuestasHabilitadas.objects.all(),
        'host': f'{request.scheme}://{request.get_host()}',
    }
    return render(request, 'encuestas/administrar_habilitadas.html', context)


@login_required
@permission_required('dborrador.add_asignacion')
def borrar_habilitacion(request, habilitacion_id):
    EncuestasHabilitadas.objects.get(pk=habilitacion_id).delete()
    return HttpResponseRedirect(reverse('encuestas:administrar_habilitadas'))


@login_required
@permission_required('dborrador.add_asignacion')
def agregar_habilitacion(request):
    if request.method == 'POST':
        form = HabilitacionDeEncuestaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('encuestas:administrar_habilitadas'))
    else:
        context = {'form': HabilitacionDeEncuestaForm()}
        return render(request, 'encuestas/agregar_habilitacion.html', context)


@login_required
@permission_required('dborrador.add_asignacion')
def cambiar_habilitacion(request, habilitacion_id):
    habilitacion =  EncuestasHabilitadas.objects.get(pk=habilitacion_id)
    if request.method == 'POST':
        form = HabilitacionDeEncuestaForm(request.POST, instance=habilitacion)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('encuestas:administrar_habilitadas'))
        else:
            logger.error(form.errors)

    else:
        form = HabilitacionDeEncuestaForm(instance=habilitacion)

    context = {'form': form, 'habilitacion': habilitacion}
    return render(request, 'encuestas/cambiar_habilitacion.html', context)


def _turnos_maximos_por_cuatrimestre(cuatrimestre):
    # DEPRECATED
    maximos = {
        Cuatrimestres.V.name: 2,
        Cuatrimestres.P.name: 5,
        Cuatrimestres.S.name: 5
    }
    return maximos[cuatrimestre]


def _turnos_minimos_por_cuatrimestre(cuatrimestre, docente):
    # DEPRECATED
    # return _turnos_maximos_por_cuatrimestre(cuatrimestre)
    return 3 if docente.es_simple and cuatrimestre != 'V' else _turnos_maximos_por_cuatrimestre(cuatrimestre)


def _nombre_cuat_error(cuatrimestre):
    nombres = {
        Cuatrimestres.V.name: 'de verano',
        Cuatrimestres.P.name: '1',
        Cuatrimestres.S.name: '2'
    }
    return nombres[cuatrimestre]

def checkear_y_salvar(datos, anno, cuatrimestres, tipo_docente, docente):
    fecha_encuesta = timezone.now()
    # docente = Docente.objects.get(pk=datos['docente'])
    opcc = EncuestasHabilitadas.objects.get(anno=anno,cuatrimestres=cuatrimestres,tipo_docente=tipo_docente).opciones()

    tdict = {} # para guardar la cantidad opciones ofrecidas

    # chequeos
    for c in cuatrimestres:
        opc = opcc[1] if c == 'V' else opcc[0]
        tmin = opc['tminS'] if docente.es_simple else opc['tmin']
        tmax = opc['tmax']
        tdif = opc['tdif']
            
        cuenta = Counter(datos.get(f'opcion{c}{o}', '-1')
                         for o in range(1, tmax+1))
        cuenta.pop('-1', None)  # descarto opciones no completadas
        if any(v > 1 for v in cuenta.values()):
            raise ValidationError('Hay turnos repetidos', code='invalid')

        cuenta_dif = Counter(datos.get(f'opcion{c}{o}', '-1')
                         for o in range(1, tdif+1))
        cuenta_dif.pop('-1', None)  # descarto opciones no completadas

        cargas = int(datos[f'cargas{c}'])

        if cargas ==  0 and sum(cuenta.values()) > 0:
            raise ValidationError(f'Si la cantidad de cargas para el cuatrimestre {_nombre_cuat_error(c)} es 0, los turnos preferidos para ese cuatrimestre deben quedar vacíos')

        if cargas > 0 and sum(cuenta_dif.values()) < tdif:
            raise ValidationError(f'Ninguna de las primeras {tdif} opciones para el cuatrimestre {_nombre_cuat_error(c)} puede quedar vacía')

        if cargas > 0 and sum(cuenta.values()) < tmin:
            raise ValidationError(f'La cantidad mínima de turnos para el cuatrimestre {_nombre_cuat_error(c)} es {tmin}')

        tdict[c] = sum(cuenta.values())

    email = datos['email']
    telefono = datos['telefono']

    email_validator = EmailValidator(message='La dirección de email es incorrecta')
    email_validator(email)
    telefono_validator(telefono)

    # OtrosDatos
    otros_datos = OtrosDatos.objects.create(docente=docente, anno=anno, cuatrimestre=cuatrimestres,
                                            tipo_docente=tipo_docente,
                                            fecha_encuesta=fecha_encuesta, comentario=datos['comentario'],
                                            email=email, telefono=telefono,
                                            cargas_declaradas=int(datos['cargas_declaradas'])
                                            )

    #  PreferenciasDocente
    opciones = {}
    pedidas = {}
    for cuatrimestre in cuatrimestres:
        tmax = tdict[cuatrimestre] # cantidad de turnos ofrecidos este cuatrimestre
        # CargasPedidas
        cargas = int(datos[f'cargas{cuatrimestre}'])
        cargas_pedidas = CargasPedidas.objects.create(docente=docente, anno=anno, cuatrimestre=cuatrimestre,
                                                      tipo_docente=tipo_docente,
                                                      fecha_encuesta=fecha_encuesta, cargas=cargas)
        pedidas[Cuatrimestres[cuatrimestre]] = cargas

        opciones_cuat = []
        for opcion in range(1, tmax + 1):
            opcion_id = int(datos[f'opcion{cuatrimestre}{opcion}'])
            if opcion_id >= 0:
                turno = Turno.objects.get(pk=opcion_id)
                peso = float(datos[f'peso{cuatrimestre}{opcion}'])
                logger.debug('miro preferencia de docente: %s, turno: %s, peso: %s, fecha: %s',
                             docente, turno, peso, fecha_encuesta)

                pref = PreferenciasDocente.objects.create(docente=docente, turno=turno,
                                                          tipo_docente=tipo_docente,
                                                          peso=peso, fecha_encuesta=fecha_encuesta)
                logger.info('Agrego preferencia de docente: %s, turno: %s, peso: %s, fecha: %s',
                            docente, turno, peso, fecha_encuesta)
                opciones_cuat.append(pref)
        opciones[Cuatrimestres[cuatrimestre]] = opciones_cuat
    return opciones, otros_datos, pedidas


DocenteParaEncuesta = namedtuple('DocenteParaEncuesta', ['id', 'nombre'])
TurnoParaEncuesta = namedtuple('TurnoParaEncuesta', ['id', 'texto', 'dificil_de_cubrir', 'no_elegible'])
OpcionesParaEncuesta = namedtuple('OpcionesParaEncuesta', ['numero', 'lista_corta', 'turno_elegido', 'peso'])
OpcionesPorCuatrimestre = namedtuple('OpcionesPorCuatrimestre', ['opciones', 'turnos'])


def _generar_docentes(anno, cuatrimestres, tipo_docente):
    tipo = TipoDocentes[tipo_docente]
    docentes = [DocenteParaEncuesta(-1, '')]
    docentes += [DocenteParaEncuesta(docente.id, docente.apellido_nombre)
                 for docente in sorted(Mapeos.docentes_de_tipo(tipo, anno, cuatrimestres),
                                       key=lambda d: strxfrm(d.apellido_nombre))]
    return docentes


def _generar_contexto(anno, cuatrimestre, tipo_docente, cuatrimestres):
    tipo = TipoDocentes[tipo_docente]
    ac = AnnoCuatrimestre(anno, cuatrimestre)
    turnos_ac = Mapeos.turnos_de_tipo_y_ac(tipo, ac)
    necesidades = Mapeos.turno_y_necesidad(tipo, ac)

    turnos = [TurnoParaEncuesta(-1, '', True, False)]
    turnos += [TurnoParaEncuesta(turno.id, f'{turno} ({turno.horarios_info().diayhora or "sin horario"})',
                                 turno.dificil_de_cubrir, Mapeos.necesidades_no_cubiertas(turno, tipo) <= 0)
               for turno in sorted(turnos_ac, key=lambda t: (strxfrm(t.materia.nombre), t.numero))]

    opc = EncuestasHabilitadas.objects.get(anno=anno,cuatrimestres=cuatrimestres,tipo_docente=tipo_docente).opciones()
    opc = opc[1] if cuatrimestre == 'V' else opc[0]
    cantidad_de_opciones = opc['tmax']
    cantidad_de_dificiles = opc['tdif']
    opciones = [OpcionesParaEncuesta(i, i <= cantidad_de_dificiles, -1, 1)
                for i in range(1, cantidad_de_opciones + 1)]

    return OpcionesPorCuatrimestre(opciones, turnos)


def _modificar_contexto_con_datos_request(context, datos):
    nuevas_opciones_turnos = {}
    for cuatrimestre, opciones_turnos_cuat in context['opciones_por_cuatrimestre'].items():
        opciones_cuatrimestre = []
        for opcion, dificil, _, _ in opciones_turnos_cuat.opciones:
            elegido = int(datos[f'opcion{cuatrimestre.name}{opcion}'])
            peso = datos[f'peso{cuatrimestre.name}{opcion}']
            opciones_cuatrimestre.append(OpcionesParaEncuesta(opcion, dificil, elegido, peso))
        nuevas_opciones_turnos[cuatrimestre] = OpcionesPorCuatrimestre(opciones_cuatrimestre,
                                                                       opciones_turnos_cuat.turnos)
    context['opciones_por_cuatrimestre'] = nuevas_opciones_turnos

    cargas_cuatrimestre = [f'cargas{c.name}' for c in context['opciones_por_cuatrimestre']]
    for campo in ['email', 'telefono', 'comentario', *cargas_cuatrimestre]:
        context[campo] = datos[campo]

    context['docente_selected'] = int(datos['docente'])


def _encuesta_con_mensaje_de_error(request, context, mensaje):
        messages.error(request, mensaje)
        _modificar_contexto_con_datos_request(context, request.POST)
        return render(request, 'encuestas/encuesta.html', context)


def mandar_mail(opciones, otros_datos, cargas_pedidas, anno, cuatrimestres, tipo_docente):
    subject = f'encuesta para {tipo_docente}, año {anno}, cuatrimestres: {cuatrimestres}'

    mensaje = ''
    for cuatrimestre, lista in opciones.items():
        mensaje += f'\n\nCuatrimestre: {cuatrimestre.value}'
        mensaje += f'\n  Turnos que quiere cubrir: {cargas_pedidas[cuatrimestre]}'
        for preferencia in lista:
            mensaje += f'\n\n    Turno: {preferencia.turno} ({preferencia.turno.horarios_info().diayhora or "sin horario"})'
            mensaje +=   f'\n    Peso:  {preferencia.peso}'

    mensaje += f'\n\nComentarios:\n{otros_datos.comentario}'
    mensaje += f'\n\nDatos:'
    mensaje += f'\n  email:    {otros_datos.email}'
    mensaje += f'\n  teléfono: {otros_datos.telefono}'

    try:
        send_mail(subject, mensaje, settings.EMAIL_HOST_USER, [otros_datos.email])
    except Exception as e:  # TODO: poner una excepción adecuada
        logger.exception('no puedo mandar el mail')

#login 
def obtener_cargas_para_encuesta(docente, anno, cuatrimestres):
    """
    Obtiene las cargas ASIGNADAS de un docente solo para los cuatrimestres
    de la encuesta actual.
    """
    cargas = {}
    
    for cuatrimestre in cuatrimestres:
        cargas_cuat = Carga.objects.filter(
            docente=docente,
            anno=anno,
            cuatrimestre=cuatrimestre
        )
        
        cargas[cuatrimestre] = sum(c.carga for c in cargas_cuat)
            
    return cargas

@docente_autenticado_required
def encuesta(request, anno, cuatrimestres, tipo_docente, docente_autenticado=None):
    if not EncuestasHabilitadas.esta_habilitada(anno, cuatrimestres, tipo_docente, timezone.now()):
        return HttpResponse(status=403, content="La encuesta que querés llenar no está habilitada.")

    opciones_por_cuatrimestre = {Cuatrimestres[cuatri]: _generar_contexto(anno, cuatri, tipo_docente, cuatrimestres)
                                 for cuatri in cuatrimestres}

    #login
    docente = docente_autenticado
    cargas_por_cuatri = obtener_cargas_para_encuesta(docente, anno, cuatrimestres)
    cargas_total = sum(cargas_por_cuatri.values())
    #login

    context = {
        #login
        'docente': docente,  # Ahora solo un docente, no una lista
        'docente_nombre': getattr(docente, 'nombre', 'Docente'),
        'docente_email': docente.email,
        'cargas': cargas_total,
        #login
        'docentes': _generar_docentes(anno, cuatrimestres, tipo_docente),
        'opciones_por_cuatrimestre': opciones_por_cuatrimestre,
        'anno': anno,
        'cuatrimestres': cuatrimestres,
        'cuatrimestres_texto': GrupoCuatrimestral[cuatrimestres].value,
        'tipo_docente': tipo_docente,
        'maximo_peso': 20,
        'email': '', 'telefono': '', 'comentario': '',
        #login
        # 'docente_selected': -1,
        #login
        f'cargas{Cuatrimestres.V.name}': 0,
        f'cargas{Cuatrimestres.P.name}': 1,
        f'cargas{Cuatrimestres.S.name}': 1,
    }

    #login
    # try:
    #     docente = Docente.objects.get(pk=request.POST['docente'])
    # except (ValueError, KeyError):
    #     return render(request, 'encuestas/encuesta.html', context)
    # except Docente.DoesNotExist:
    #     return _encuesta_con_mensaje_de_error(request, context, "No me dijiste quién sos")
    #login
    if request.method == 'GET':
        # ⭐ SOLO para GET: mostrar formulario vacío/prellenado
        return render(request, 'encuestas/encuesta.html', context)

    elif request.method == 'POST':

        try:
            opciones, otros_datos, cargas_pedidas = checkear_y_salvar(request.POST,
                                                                      anno, cuatrimestres,
                                                                      tipo_docente,
                                                                      docente)
            mandar_mail(opciones, otros_datos, cargas_pedidas, anno, cuatrimestres, tipo_docente)
            return render(request,
                          'encuestas/final.html',
                          context={'opciones': opciones, 'docente': docente,
                                   'email': otros_datos.email,
                                   'telefono': otros_datos.telefono,
                                   'comentario': otros_datos.comentario,
                                   'anno': anno})
        except ValidationError as e:
            return _encuesta_con_mensaje_de_error(request, context, e.message)


@login_required
@permission_required('dborrador.add_asignacion')
def ver_resultados_de_encuestas(request, anno, cuatrimestre):
    cuenta_encuestas = Count('cargaspedidas', filter=Q(cargaspedidas__anno=anno,
                                                       cargaspedidas__cuatrimestre=cuatrimestre,
                                                       cargaspedidas__cargas__gt=-1))
    docentes_con_pedidos = Docente.objects.annotate(pedidos=cuenta_encuestas) \
                                  .filter(pedidos__gt=0) \
                                  .order_by('-pedidos', 'na_apellido', 'na_nombre')
    return render(request, 'encuestas/resultados_de_encuestas.html',
                  {'anno': anno, 'cuatrimestre': Cuatrimestres[cuatrimestre],
                   'docentes': docentes_con_pedidos,
                   })


@login_required
@permission_required('dborrador.add_asignacion')
def encuestas_de_un_docente(request, docente_id, anno, cuatrimestre):
    docente = Docente.objects.get(pk=docente_id)

    fechas = {cp.fecha_encuesta
              for cp in CargasPedidas.objects.filter(docente=docente, anno=anno, cuatrimestre=cuatrimestre)}

    preferencias = {fecha: (PreferenciasDocente.objects.filter(docente=docente,
                                                               turno__anno=anno, turno__cuatrimestre=cuatrimestre,
                                                               fecha_encuesta=fecha),
                            CargasPedidas.objects.get(docente=docente, anno=anno, cuatrimestre=cuatrimestre,
                                                      fecha_encuesta=fecha).cargas
                            )
                    for fecha in sorted(fechas, reverse=True)}
    otros_datos = OtrosDatos.objects.filter(docente=docente, anno=anno, cuatrimestre__contains=cuatrimestre) \
                                    .order_by('-fecha_encuesta')


    return render(request, 'encuestas/encuestas_de_un_docente.html',
                  {'anno': anno, 'cuatrimestre': Cuatrimestres[cuatrimestre],
                   'docente': docente,
                   'preferencias': preferencias,
                   'otros_datos': otros_datos,
                   })
