from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.conf.urls.static import static
from django.conf import settings

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
    path('password_reset_done/' , 
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
    path('subir-firma/', views.subir_firma, name='subir_firma'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("buscar/", views.buscar_curso, name="buscar_curso"),
    path("coordinador/", views.coordinador, name="coordinador"),
    path("reportes/", views.reportes, name="reportes"),
    path("generate_reports/<int:curso_id>/", views.generate_reports, name="generate_reports"),

    
     # Generar curso
    path('generar_curso/', views.generar_curso, name='generar_curso'),
    # Obtener datos del programa
    path("get-programa/<int:programa_id>/", views.get_programa, name="get_programa"),
    # Obtener municipios por departamento
    path("get-municipios/<int:departamento_id>/", views.get_municipios, name="get_municipios"),
    path("tipo-oferta/", views.tipo_oferta, name="tipo_oferta"),
    path("generar-curso/<str:tipo>/", views.generar_curso, name="generar_curso"),

    
    # aprobar - rechazar solicitudes
    path("solicitud/<int:pk>/aprobar/", views.approve_request, name="approve_request"),
    path("solicitud/<int:pk>/rechazar/", views.reject_request, name="reject_request"),
    

    # Registrar aspirante a un curso
    path("curso/<int:curso_id>/aspirantes/", views.registrar_aspirante, name="registrar_aspirante"),
    # Página que muestra el ID del curso y la URL para registrar aspirantes
    path("curso-generado/", views.curso_generado, name="curso_generado"),
    # Descargar archivo Word generado
    path("curso/<int:curso_id>/descargar/", views.descargar_curso, name="descargar_curso"),
    # Eliminar curso
    path("eliminar/<int:curso_id>/", views.eliminar_curso, name="eliminar_curso"),
    # Procesar OCR para un aspirante
    path("curso/ocr/", views.ocr_aspirante, name="ocr_aspirante"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)