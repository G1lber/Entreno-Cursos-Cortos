from django.shortcuts import redirect, get_object_or_404
from .models import TipoDocumento, Rol, Usuario,Programa, Departamento, Municipio, Curso, Solucitud
from .forms import UsuarioEditForm, UsuarioCreateForm, InicioSesionForm, CursoForm
from django.urls import reverse
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
from django.db.models import Q, OuterRef, Subquery # Importar Q para búsquedas complejas
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime, timedelta
from openpyxl import load_workbook
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError

def dashboard(request):
    return render(request, 'dashboard.html')

#Buscar Cursos
def buscar_curso(request):
    q = request.GET.get("q", "").strip()
    courses = []

    if q:
        courses = Curso.objects.filter(
            Q(programa__nombre__icontains=q) |
            Q(usuario__first_name__icontains=q) |
            Q(usuario__last_name__icontains=q) |
            Q(usuario__documento__icontains=q)
        )

        # mapear estado numérico a texto
        estado_map = {0: "pending", 1: "approved", 2: "rejected"}
        for c in courses:
            c.status = estado_map.get(c.estado, "pending")
            c.registrationLink = c.link  # 👈 usar el campo `link` del modelo

    return render(request, "buscar_curso.html", {
        "courses": courses,
        "q": q
    })
#Eliminar Curso
def eliminar_curso(request, curso_id):
    if request.method == "POST":
        curso = get_object_or_404(Curso, id=curso_id)
        curso.delete()
        messages.success(request, f"El curso {curso.programa.nombre} fue eliminado correctamente.")
    return redirect("buscar_curso")
    
#Coordinador
def coordinador(request):
    solicitudes = Solucitud.objects.select_related("curso__programa", "curso__usuario")

    # Creamos un diccionario de traducción
    estado_map = {
        0: "pending",
        1: "approved",
        2: "rejected",
    }

    # Agregamos un atributo extra a cada objeto
    for s in solicitudes:
        s.status = estado_map.get(s.estado, "unknown")

    pending_courses = [s for s in solicitudes if s.estado == 0]
    approved_courses = [s for s in solicitudes if s.estado == 1]
    rejected_courses = [s for s in solicitudes if s.estado == 2]
    return render(request, 'coordinador_dashboard.html',
                  { "pending_courses": pending_courses,
                    "approved_courses": approved_courses,
                    "rejected_courses": rejected_courses,
                    "courses": solicitudes,
                    })
    
#Aprobar-Rechazar Solicitudes
def approve_request(request, pk):
    solicitud = get_object_or_404(Solucitud, pk=pk)
    solicitud.estado = 1  # aprobado
    solicitud.save()
    return redirect("coordinador")  

def reject_request(request, pk):
    solicitud = get_object_or_404(Solucitud, pk=pk)
    solicitud.estado = 2  # rechazado
    solicitud.save()
    return redirect("coordinador")

#Reportes
def reportes(request):
    cursos = Curso.objects.all().order_by('-fecha_inicio')
    return render(request, 'reportes.html', {'cursos': cursos})

def generate_reports(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Curso, id=course_id)

        # Reporte 1 en plantilla XLSM
        ruta_plantilla = os.path.join(
            settings.BASE_DIR,
            "curso", "templates", "docs", "Masivo 2024 MOISO.xlsm"
        )

        wb = load_workbook(ruta_plantilla, keep_vba=True)
        ws = wb.active  # puedes usar ws = wb["Hoja1"] si tu hoja tiene nombre

        # Traer aspirantes relacionados al curso
        aspirantes = course.aspirante_set.all()  # FK Curso → Aspirante

        fila = 5  # empieza a llenar desde fila 5
        for asp in aspirantes:
            ws[f"B{fila}"] = asp.tipo_documento.nombre if asp.tipo_documento else ""
            ws[f"C{fila}"] = asp.documento
            ws[f"D{fila}"] = getattr(asp, "tipo_poblacion", "Estudiante")  # ejemplo

            # 🔹 Dejar F y G vacías
            ws[f"F{fila}"] = ""
            ws[f"G{fila}"] = ""

            fila += 1

        reporte1 = BytesIO()
        wb.save(reporte1)
        reporte1.seek(0)

        #Reporte 2 con pandas
        aspirantes_data = [
            [
                asp.tipo_documento.nombre if asp.tipo_documento else "",
                asp.documento,
                asp.first_name,
                asp.last_name,
                asp.email,
                getattr(asp, "celular", ""),  # si tienes un campo teléfono
                course.programa.nombre if course.programa else "",
            ]
            for asp in aspirantes
        ]

        df2 = pd.DataFrame(
            aspirantes_data,
            columns=[
                "Tipo Documento",
                "Documento",
                "Nombre",
                "Apellido",
                "Email",
                "Número",
                "Programa",
            ],
        )

        reporte2 = BytesIO()
        df2.to_excel(reporte2, index=False)
        reporte2.seek(0)

        #Empaquetar ZIP
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            # Guardar reporte 1
            zip_file.writestr(
                f"reporte1_{course.programa.nombre if course.programa else 'curso'}.xlsm",
                reporte1.getvalue(),
            )
            # Guardar reporte 2
            zip_file.writestr(
                f"reporte2_{course.programa.nombre if course.programa else 'curso'}.xlsx",
                reporte2.getvalue(),
            )

        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/zip")
        response[
            "Content-Disposition"
        ] = f'attachment; filename=\"reportes_{course.programa.nombre if course.programa else 'curso'}.zip\"'
        return response

    return redirect("reportes")

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

    # 👇 Guardar la URL en el modelo si existe
    if url_aspirantes:
        curso.link = url_aspirantes
        curso.save(update_fields=["link"])

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
            # Autenticar al usuario con el email y password
            usuario = authenticate(request, email=email, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f"Inicio de sesión exitoso para {email}.")
                
                # Redirigir según el rol del usuario
                if usuario.rol.nombre == "INSTRUCTOR":
                    return redirect('dashboard')  # Dashboard para instructores
                elif usuario.rol.nombre == "FUNCIONARIO":
                    return redirect('dashboard')  # Panel de coordinación para funcionarios
                elif usuario.rol.nombre == "Admin" or usuario.is_superuser:
                    return redirect('viewUsuarios')  # Vista de administración para admins
                else:
                    # Redirección por defecto para otros roles no especificados
                    return redirect('dashboard')
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

@login_required
def subir_firma(request):
    if request.method == 'POST':
        archivo = request.FILES.get('firma')
        
        if archivo:
            # Validar tipo de archivo
            if archivo.content_type not in ['image/png', 'image/jpeg']:
                messages.error(request, "Formato no válido. Use PNG o JPG")
                return redirect('subir_firma')
            
            # Validar dimensiones de la imagen
            try:
                width, height = get_image_dimensions(archivo)
                if width > 500 or height > 200:
                    messages.error(request, "La imagen no debe exceder 500x200 píxeles")
                    return redirect('subir_firma')
            except Exception:
                messages.error(request, "Error al procesar la imagen")
                return redirect('subir_firma')
            
            # Guardar la firma
            usuario = request.user
            primera_vez = not bool(usuario.firma_digital)
            
            usuario.firma_digital = archivo
            usuario.save()
            
            if primera_vez:
                messages.success(request, "Firma digital registrada correctamente")
            else:
                messages.success(request, "Firma digital actualizada correctamente")
            
            return redirect('dashboard')
        else:
            messages.error(request, "Debe seleccionar un archivo")
    
    return render(request, 'subir_firma.html')