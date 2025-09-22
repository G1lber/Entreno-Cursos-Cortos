from django.contrib import admin
from .models import (
    Departamento, Municipio, Programa, Rol, TipoDocumento,
    Usuario, Curso, Solicitud
)

# ----------------------------
# Modelos básicos
# ----------------------------
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'departamento')
    search_fields = ('nombre',)
    list_filter = ('departamento',)

@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo', 'duracion')
    search_fields = ('nombre', 'codigo')

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

# ----------------------------
# Usuario personalizado
# ----------------------------
from django.contrib.auth.admin import UserAdmin

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'documento', 'first_name', 'last_name', 'rol', 'tipo_documento', 'is_active', 'is_staff')
    list_filter = ('rol', 'tipo_documento', 'is_staff', 'is_active')
    search_fields = ('email', 'documento', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'documento', 'tipo_documento', 'rol', 'firma_digital')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'documento', 'tipo_documento', 'rol', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

# ----------------------------
# Cursos
# ----------------------------
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'programa', 'usuario', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('programa', 'estado', 'fecha_inicio')
    search_fields = ('usuario__email', 'programa__nombre')

# ----------------------------
# Solicitudes
# ----------------------------
@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'curso', 'estado')
    list_filter = ('estado', 'curso__programa')
    search_fields = ('curso__usuario__email',)
