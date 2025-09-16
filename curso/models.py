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


class Usuario(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="usuarios"
    )
    documento = models.CharField(max_length=50, null=True, blank=True)
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="usuarios"
    )
    correo = models.EmailField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    firma = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()


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
    estado = models.IntegerField(null=True, blank=True)

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
