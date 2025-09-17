from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
urlpatterns = [
    

    path('', views.inicioSesion, name='inicioSesion'),
    # formulario para ingresar correo
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='layout/password_reset_form.html',
             email_template_name='layout/password_reset_email.html',
             success_url=reverse_lazy('password_reset_done')  # <--- corregido
         ), 
         name='password_reset'),

    # mensaje de éxito
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='layout/password_reset_done.html'
         ), 
         name='password_reset_done'),

    # link de recuperación
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='layout/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')  # <--- corregido
         ), 
         name='password_reset_confirm'),

    # confirmación de cambio
    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='layout/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('logout/', views.log_out, name='logout'),
    path('usuario/', views.usuario, name='usuario'),
    path('usuario/create/', views.createUsuario, name='createUsuario'),
    path('usuario/view/', views.viewUsuarios, name='viewUsuarios'),
    path('usuario/edit/<int:id>/', views.editUsuario, name='editUsuario'),
    path("usuarios/toggle/<int:id>/", views.toggle_usuario, name="toggleUsuario"),
    path('generar_curso/', views.generar_curso, name='generar_curso'),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("buscar/", views.buscar_curso, name="buscar_curso"),
    path("coordinador/", views.coordinador, name="coordinador"),
    path("reportes/", views.reportes, name="reportes"),
]
