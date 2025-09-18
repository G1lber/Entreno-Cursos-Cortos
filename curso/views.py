from django.shortcuts import redirect, get_object_or_404
from .models import TipoDocumento, Rol, Usuario,Programa, Departamento, Municipio, Curso
from .forms import UsuarioEditForm, UsuarioCreateForm, InicioSesionForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, FileResponse
from .forms import CursoForm, AspiranteForm
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

import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from docxtpl import DocxTemplate
from .forms import CursoForm
from .models import Curso


from django.urls import reverse

def generar_curso(request):
    usuario = request.user  # Usuario autenticado

    if request.method == "POST":
        form = CursoForm(request.POST, request.FILES, usuario=usuario)
        if form.is_valid():
            try:
                # ✅ Crear curso en BD
                programa = form.cleaned_data["nombreprograma"]
                fecha_inicio = form.cleaned_data["fechainicio"]
                fecha_fin = form.cleaned_data["fechafin"]

                curso = Curso.objects.create(
                    programa=programa,
                    usuario=usuario,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                )

                # ✅ Preparar documento
                contexto = form.cleaned_data
                contexto.update({
                    "nombre": f"{usuario.first_name} {usuario.last_name}".strip(),
                    "tipodoc": usuario.tipo_documento.nombre if usuario.tipo_documento else "",
                    "numerodoc": usuario.documento,
                    "correo": usuario.email,
                    "curso_id": curso.id,
                })

                ruta_base = os.path.join(settings.BASE_DIR, "curso", "templates", "docs")
                ruta_plantilla = os.path.join(ruta_base, "plantilla-curso.docx")
                if not os.path.exists(ruta_plantilla):
                    raise FileNotFoundError(f"No se encontró la plantilla en: {ruta_plantilla}")

                ruta_curso = os.path.join(ruta_base, str(curso.id))
                os.makedirs(ruta_curso, exist_ok=True)

                # ✅ Renderizar documento
                doc = DocxTemplate(ruta_plantilla)
                doc.render(contexto)

                nombre_docx = f"curso_{curso.id}.docx"
                ruta_docx = os.path.join(ruta_curso, nombre_docx)
                doc.save(ruta_docx)

                # ✅ Guardar carta si se adjunta
                carta_file = request.FILES.get("carta_empresa")
                if carta_file:
                    nombre_carta = f"carta_{curso.id}{os.path.splitext(carta_file.name)[1]}"
                    ruta_carta = os.path.join(ruta_curso, nombre_carta)
                    with open(ruta_carta, "wb+") as destino:
                        for chunk in carta_file.chunks():
                            destino.write(chunk)
                    curso.carta = f"docs/{curso.id}/{nombre_carta}"

                curso.caracterizacion = f"docs/{curso.id}/{nombre_docx}"
                curso.save(update_fields=["caracterizacion", "carta"])

                # ✅ Generar URL de aspirantes
                url_aspirantes = request.build_absolute_uri(
                    reverse("registrar_aspirante", args=[curso.id])
                )

                # ✅ Guardar en la sesión
                request.session["curso_id"] = curso.id
                request.session["url_aspirantes"] = url_aspirantes
                request.session["ruta_docx"] = curso.caracterizacion

                # 👉 Redirigir a página de confirmación
                return redirect("curso_generado")

            except Exception as e:
                return HttpResponse(f"Error generando el documento: {e}", status=500)

    else:
        form = CursoForm(usuario=usuario)

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
# Página que muestra el ID del curso y la URL para registrar aspirantes
def curso_generado(request):
    curso_id = request.session.get("curso_id")
    url_aspirantes = request.session.get("url_aspirantes")

    if not curso_id:
        return redirect("generar_curso")

    curso = Curso.objects.select_related("programa").get(id=curso_id)

    return render(request, "formularios/curso_generado.html", {
        "curso": curso,
        "url_aspirantes": url_aspirantes,
    })
# Registrar aspirante a un curso
def registrar_aspirante(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == "POST":
        form = AspiranteForm(request.POST)
        if form.is_valid():
            aspirante = form.save(commit=False)
            aspirante.curso = curso
            aspirante.save()
            return redirect("aspirante_exito")  # Puedes hacer que vaya a una página de éxito
    else:
        form = AspiranteForm()

    return render(request, "formularios/registrar_aspirante.html", {
        "curso": curso,
        "form": form
    })
# Descargar documento generado
def descargar_curso(request, curso_id):
    try:
        curso = Curso.objects.get(id=curso_id)
        ruta_docx = os.path.join(settings.BASE_DIR, "curso", "templates", curso.caracterizacion)

        if not os.path.exists(ruta_docx):
            raise Http404("Archivo no encontrado")

        return FileResponse(
            open(ruta_docx, "rb"),
            as_attachment=True,
            filename=f"curso_{curso.id}.docx"
        )

    except Curso.DoesNotExist:
        raise Http404("Curso no existe")

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

