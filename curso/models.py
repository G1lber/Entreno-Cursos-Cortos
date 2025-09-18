from django.db import models

# Create your models here.
from django.db import models


class Departamento(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre or ""


class Municipio(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="municipios"
    )

    def __str__(self):
        return self.nombre or ""


class Programa(models.Model):
    codigo = models.IntegerField(unique=True, null=True, blank=True)
    duracion = models.CharField(max_length=50, null=True, blank=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    version = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return self.nombre or ""


class Rol(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre or ""


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre or ""


from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UsuarioManager
class Usuario(AbstractUser):
    username = None  # Eliminamos username, usamos email
    email = models.EmailField("correo electrónico", max_length=50,unique=True)


    tipo_documento = models.ForeignKey(
        "TipoDocumento",
        on_delete=models.CASCADE,
        related_name="usuarios"
    )
    documento = models.CharField(max_length=20, unique=True)  # obligatorio y único
    rol = models.ForeignKey(
        "Rol",
        on_delete=models.CASCADE,
        related_name="usuarios"
    )
    firma = models.FileField(upload_to="firmas/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # para createsuperuser

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.email} - {self.documento}"
class Curso(models.Model):
    programa = models.ForeignKey(
        Programa,
        on_delete=models.CASCADE,
        related_name="cursos"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cursos"
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    max_inscripciones = models.IntegerField(default=25)
    estado = models.IntegerField(null=True, blank=True)
    caracterizacion = models.CharField(max_length=50, null=True, blank=True)
    carta = models.CharField(max_length=50, null=True, blank=True)
    pdf_documentos = models.CharField(max_length=50, null=True, blank=True)
    aspirantes = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Curso {self.id} - {self.programa}"


class Solucitud(models.Model):  # Ojo: en SQL está escrito "solucitud", no "solicitud"
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="solucitudes"
    )
    estado = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Solucitud {self.id} - Curso {self.curso_id}"
