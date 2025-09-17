from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'layout/index.html')

def crear_curso(request):
    return render(request, 'crear_curso.html')