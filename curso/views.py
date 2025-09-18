from django.shortcuts import redirect, get_object_or_404
from .models import TipoDocumento, Rol, Usuario,Programa, Departamento, Municipio, Curso
from .forms import UsuarioEditForm, UsuarioCreateForm, InicioSesionForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import CursoForm
import os
import io
from django.conf import settings
from django.shortcuts import render
from docxtpl import DocxTemplate
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime, timedelta
from django.http import HttpResponse


def dashboard(request):
    return render(request, 'dashboard.html')

#Buscar Cursos
def buscar_curso(request):
    return render(request, 'buscar_curso.html')

#Coordinador
def coordinador(request):
    return render(request, 'coordinador_dashboard.html')

#Reportes
# Datos de ejemplo para cursos (en memoria)
EXAMPLE_COURSES = [
    {
        'id': 1,
        'program': 'Programa de Formación Ejemplo 1',
        'instructorName': 'Juan Pérez',
        'isActive': True,
        'reportsGenerated': False,
        'startDate': datetime.now().date(),
        'registrations': 25,
        'maxRegistrations': 25,
        'selectedDays': ['Lunes', 'Miércoles', 'Viernes'],
        'schedule': '14:00 - 16:00'
    },
    {
        'id': 2,
        'program': 'Programa de Formación Ejemplo 2',
        'instructorName': 'María García',
        'isActive': True,
        'reportsGenerated': True,
        'startDate': (datetime.now() + timedelta(days=10)).date(),
        'registrations': 20,
        'maxRegistrations': 25,
        'selectedDays': ['Martes', 'Jueves'],
        'schedule': '16:00 - 18:00'
    },
    {
        'id': 3,
        'program': 'Programa de Formación Ejemplo 3',
        'instructorName': 'Carlos Rodríguez',
        'isActive': False,
        'reportsGenerated': False,
        'startDate': (datetime.now() - timedelta(days=15)).date(),
        'registrations': 30,
        'maxRegistrations': 25,
        'selectedDays': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
        'schedule': '09:00 - 12:00'
    }
]

def reportes(request):
    cursos = Curso.objects.all().order_by('-fecha_inicio')
    return render(request, 'reportes.html', {'courses': cursos})

def generate_reports(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Curso, id=course_id)
        
        # Crear datos de ejemplo para los reportes (basados en tu segunda versión)
        report1_data = [
            ['CC', '12345678', 'Estudiante'],
            ['CC', '87654321', 'Profesional'],
            ['CC', '11223344', 'Estudiante'],
            ['CC', '44332211', 'Profesional'],
            ['CC', '55667788', 'Estudiante']
        ]
        df1 = pd.DataFrame(report1_data, columns=['Tipo Documento', 'Documento', 'Tipo Población'])
        
        report2_data = [
            ['CC', '12345678', 'Juan', 'Diaz', 'juan@email.com', '22222222', 'Estudiante'],
            ['CC', '111111', 'Maria', 'Diaz', 'maria@email.com', '22222222', 'Profesional'],
            ['CC', '111111', 'Gilber', 'Diaz', 'carlos@email.com', '22222222', 'Estudiante'],
            ['CC', '11111', 'Daniel',  'Diaz', 'ana@email.com', '22222222', 'Profesional'],
            ['CC', '1111', 'Fernanda', 'Diaz', 'luisa@email.com', '22222222', 'Estudiante']
        ]
        df2 = pd.DataFrame(report2_data, columns=['Tipo Documento', 'Documento', 'Nombre', 'Apellido', 'Email', 'Número', 'Programa'])
        
        # Crear archivo ZIP en memoria
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            # Guardar primer reporte
            excel_file1 = BytesIO()
            df1.to_excel(excel_file1, index=False)
            zip_file.writestr(f'reporte1_{course.programa.nombre if course.programa else "curso"}.xlsx', excel_file1.getvalue())
            
            # Guardar segundo reporte
            excel_file2 = BytesIO()
            df2.to_excel(excel_file2, index=False)
            zip_file.writestr(f'reporte2_{course.programa.nombre if course.programa else "curso"}.xlsx', excel_file2.getvalue())
        
        buffer.seek(0)
        
        # Marcar curso como con reportes generados
        course.reportes_generados = True
        course.save()
        
        # Devolver el ZIP como respuesta
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="reportes_{course.programa.nombre if course.programa else "curso"}.zip"'
        return response
    
    return redirect('reportes')

def generar_curso(request):
    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            try:
                # ✅ Obtener datos del formulario
                contexto = form.cleaned_data
                print("✅ Datos del formulario:", contexto)

                # ✅ Construir ruta absoluta de la plantilla
                ruta = os.path.join(
                    settings.BASE_DIR,
                    "curso",
                    "templates",
                    "docs",
                    "plantilla-curso.docx"
                )
                if not os.path.exists(ruta):
                    raise FileNotFoundError(f"No se encontró la plantilla en: {ruta}")

                print(f"📄 Usando plantilla: {ruta}")

                # ✅ Cargar y renderizar documento
                doc = DocxTemplate(ruta)
                doc.render(contexto)

                # ✅ Guardar en memoria
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                # ✅ Respuesta HTTP con archivo generado
                response = HttpResponse(
                    buffer,
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                response["Content-Disposition"] = 'attachment; filename="curso_generado.docx"'
                return response

            except Exception as e:
                # ⚠️ Captura cualquier error inesperado
                return HttpResponse(f"Error generando el documento: {e}", status=500)

        else:
            print("❌ Formulario inválido:", form.errors)

    else:
        form = CursoForm()

    # Si es GET o si el form es inválido, renderiza el form
    return render(request, "formularios/formulario-formato.html", {"form": form})
# Obtener datos del programa
def get_programa(request, programa_id):
    try:
        programa = Programa.objects.get(id=programa_id)
        data = {
            "codigo": programa.codigo,
            "version": programa.version,
            "duracion": programa.duracion,
        }
        return JsonResponse(data)
    except Programa.DoesNotExist:
        return JsonResponse({"error": "Programa no encontrado"}, status=404)
# Obtener datos de departamento y municipio
def get_municipios(request, departamento_id):
    municipios = Municipio.objects.filter(departamento_id=departamento_id).values("id", "nombre")
    return JsonResponse(list(municipios), safe=False)

def inicioSesion(request):
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Aquí deberías autenticar al usuario con el email y password
            usuario = authenticate(request, email=email, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f"Inicio de sesión exitoso para {email}.")
                if usuario.rol.nombre == "INSTRUCTOR":
                    return redirect('generar_curso')  # Redirige a la página principal u otra página
                return redirect('viewUsuarios')  # Redirige a la página principal u otra página
            else:
                messages.error(request, "Credenciales inválidas.")
    else:
        form = InicioSesionForm()
    return render(request, 'layout/inicioSesion.html', {'form': form})

def log_out(request):
    logout(request)  # elimina la sesión del usuario
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('inicioSesion')  

@login_required
def usuario(request):
    form = UsuarioCreateForm()
    return render(request, 'layout/usuario_form.html', {'form': form })

@login_required
def createUsuario(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('viewUsuarios')
    else:
        form = UsuarioCreateForm()
    return render(request, 'layout/usuario_form.html', {"form": form})

@login_required
def viewUsuarios(request):
    usuarios= Usuario.objects.all()
    return render(request, 'layout/viewUsuarios.html', {'usuarios': usuarios})

@login_required
def editUsuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"El usuario {usuario.email} ha sido actualizado.")
            return redirect('viewUsuarios')
    else:
        form = UsuarioEditForm(instance=usuario)
    return render(request, 'layout/usuario_form.html', {"form": form})

@login_required
def toggle_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.is_active = not usuario.is_active  # Cambiar True <-> False
    usuario.save()
    
    estado = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f"El usuario {usuario.email} ha sido {estado}.")
    return redirect("viewUsuarios")  # redirige a tu lista de usuarios

