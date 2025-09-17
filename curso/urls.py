from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('inicioSesion/', views.inicioSesion, name='inicioSesion'),
    path('logout/', views.log_out, name='logout'),
    path('usuario/', views.usuario, name='usuario'),
    path('usuario/create/', views.createUsuario, name='createUsuario'),
    path('usuario/view/', views.viewUsuarios, name='viewUsuarios'),
    path('usuario/edit/<int:id>/', views.editUsuario, name='editUsuario'),
    path("usuarios/toggle/<int:id>/", views.toggle_usuario, name="toggleUsuario"),
]
