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

def dashboard(request):
    return render(request, 'dashboard.html')

#Buscar Cursos
def buscar_curso(request):
    return render(request, 'buscar_curso.html')

#Coordinador
def coordinador(request):
    return render(request, 'coordinador_dashboard.html')

#Reportes
def reportes(request):
    return render(request, 'reportes.html')

import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from docxtpl import DocxTemplate
from .forms import CursoForm
from .models import Curso


def generar_curso(request):
    usuario = request.user  # Usuario autenticado

    if request.method == "POST":
        form = CursoForm(request.POST, usuario=usuario)
        if form.is_valid():
            try:
                # ✅ Datos mínimos para crear el curso
                programa = form.cleaned_data["nombreprograma"]
                fecha_inicio = form.cleaned_data["fechainicio"]
                fecha_fin = form.cleaned_data["fechafin"]

                # ✅ Crear curso en BD (aún sin caracterización)
                curso = Curso.objects.create(
                    programa=programa,
                    usuario=usuario,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                )

                # ✅ Preparar contexto para el documento
                contexto = form.cleaned_data
                contexto.update({
                    "nombre": f"{usuario.first_name} {usuario.last_name}".strip(),
                    "tipodoc": usuario.tipo_documento.nombre if usuario.tipo_documento else "",
                    "numerodoc": usuario.documento,
                    "correo": usuario.email,
                    "curso_id": curso.id,
                })

                # ✅ Ruta base donde está la plantilla
                ruta_base = os.path.join(
                    settings.BASE_DIR,
                    "curso",
                    "templates",
                    "docs"
                )

                # ✅ Ruta de la plantilla
                ruta_plantilla = os.path.join(ruta_base, "plantilla-curso.docx")
                if not os.path.exists(ruta_plantilla):
                    raise FileNotFoundError(f"No se encontró la plantilla en: {ruta_plantilla}")

                # ✅ Crear carpeta con el ID del curso
                ruta_curso = os.path.join(ruta_base, str(curso.id))
                os.makedirs(ruta_curso, exist_ok=True)

                # ✅ Renderizar documento
                doc = DocxTemplate(ruta_plantilla)
                doc.render(contexto)

                # ✅ Guardar archivo en la carpeta del curso
                nombre_docx = f"curso_{curso.id}.docx"
                ruta_docx = os.path.join(ruta_curso, nombre_docx)
                doc.save(ruta_docx)

                # ✅ Guardar la "URL relativa" en la BD (campo caracterizacion)
                curso.caracterizacion = f"docs/{curso.id}/{nombre_docx}"
                curso.save(update_fields=["caracterizacion"])

                # ✅ Devolver archivo como descarga
                with open(ruta_docx, "rb") as f:
                    response = HttpResponse(
                        f.read(),
                        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                response["Content-Disposition"] = f'attachment; filename="{nombre_docx}"'
                return response

            except Exception as e:
                return HttpResponse(f"Error generando el documento: {e}", status=500)

        else:
            print("❌ Formulario inválido:", form.errors)

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

