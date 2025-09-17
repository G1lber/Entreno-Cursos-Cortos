from django.shortcuts import redirect, get_object_or_404
from .models import TipoDocumento, Rol, Usuario,Programa, Departamento, Municipio
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

