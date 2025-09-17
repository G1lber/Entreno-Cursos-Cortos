from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generar_curso/', views.generar_curso, name='generar_curso'),
]