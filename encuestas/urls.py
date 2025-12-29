from django.urls import path

from . import views
from django.contrib import admin
from django.urls import include
from encuestas.views import login_view, verificar_codigo_view, logout_view, error_view

app_name = 'encuestas'
urlpatterns = [
    path('', views.index, name='index'),
    path('agregar_habilitacion',
         views.agregar_habilitacion, name='agregar_habilitacion'),
    path('cambiar_habilitacion/<int:habilitacion_id>',
         views.cambiar_habilitacion, name='cambiar_habilitacion'),
    path('borrar_habilitacion/<int:habilitacion_id>',
         views.borrar_habilitacion, name='borrar_habilitacion'),
    path('administrar_habilitadas',
         views.administrar_habilitadas, name='administrar_habilitadas'),
    path('encuesta/<int:anno>/<str:cuatrimestres>/<str:tipo_docente>',
         views.encuesta, name='encuesta'),
    path('ver_resultados_de_encuestas/<int:anno>/<str:cuatrimestre>',
         views.ver_resultados_de_encuestas, name='ver_resultados_de_encuestas'),
    path('encuestas_de_un_docente/<int:docente_id>/<int:anno>/<str:cuatrimestre>',
         views.encuestas_de_un_docente, name='encuestas_de_un_docente'),
    path('login/', login_view, name='login'),
    path('verificar-codigo/', verificar_codigo_view, name='verificar_codigo'),
    path('logout/', logout_view, name='logout'),
    path('error/', error_view, name='error_page'),
]
