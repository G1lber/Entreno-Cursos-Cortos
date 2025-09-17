from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from docxtpl import DocxTemplate
import io
from .forms import CursoForm

import os
import io
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from docxtpl import DocxTemplate
from .forms import CursoForm

def generar_curso(request):
    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            # Obtener datos
            contexto = form.cleaned_data

            # Construir ruta absoluta de la plantilla
            ruta = os.path.join(settings.BASE_DIR, "curso", "templates", "docs", "plantilla-curso.docx")
            if not os.path.exists(ruta):
                raise FileNotFoundError(f"No se encontró la plantilla en: {ruta}")

            # Cargar plantilla
            doc = DocxTemplate(ruta)
            doc.render(contexto)

            # Guardar en memoria
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Respuesta HTTP con archivo generado
            response = HttpResponse(
                buffer,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = 'attachment; filename=\"curso_generado.docx\"'
            return response
    else:
        form = CursoForm()

    return render(request, "formularios/formulario-formato.html", {"form": form})


# Create your views here.
def index(request):
    return render(request, 'layout/index.html')