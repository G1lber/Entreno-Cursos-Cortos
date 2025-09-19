from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from .managers import UsuarioManager

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

class Usuario(AbstractUser):
    username = None  # Eliminamos username, usamos email
    email = models.EmailField("correo electrónico", max_length=191, unique=True)  # Ajustado
    tipo_documento = models.ForeignKey(
        "TipoDocumento",
        on_delete=models.CASCADE,
        related_name="usuarios"
    )
    documento = models.CharField(max_length=191, unique=True)  # Ajustado
    rol = models.ForeignKey(
        "Rol",
        on_delete=models.CASCADE,
        related_name="usuarios"
    )
    firma_digital = models.ImageField(
        upload_to='firmas/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

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
    caracterizacion = models.CharField(max_length=191, null=True, blank=True)  # Ajustado
    carta = models.CharField(max_length=191, null=True, blank=True)  # Ajustado
    pdf_documentos = models.CharField(max_length=191, null=True, blank=True)  # Ajustado
    aspirantes = models.CharField(max_length=191, null=True, blank=True)  # Ajustado
    link = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"Curso {self.id} - {self.programa}"

class Solucitud(models.Model):
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

class Poblacion(models.Model):
    nombre = models.CharField("Nombre", max_length=191, unique=True)  # Ajustado

    class Meta:
        verbose_name = "Población"
        verbose_name_plural = "Poblaciones"

    def __str__(self):
        return self.nombre
    
class Aspirante(models.Model):
    nombre = models.CharField("Nombre", max_length=150)
    correo = models.EmailField("Correo", max_length=191, unique=True)  # Ajustado
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    poblacion = models.ForeignKey(
        Poblacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="aprendices"
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True, related_name="aprendices"
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="aprendices"
    )
    documento = models.CharField("Documento", max_length=191, unique=True)  # Ajustado
    archivo_documento = models.FileField("Archivo Documento", upload_to="documentos/", blank=True, null=True)

    class Meta:
        verbose_name = "Aspirante"
        verbose_name_plural = "Aspirantes"

    def __str__(self):
        return f"{self.nombre} ({self.documento})"
