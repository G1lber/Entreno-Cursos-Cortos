from django.contrib.auth.base_user import BaseUserManager
from django.utils.crypto import get_random_string

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)

        # Defaults para los campos requeridos
        from .models import TipoDocumento, Rol  # evitar import circular

        if "tipo_documento" not in extra_fields or not extra_fields["tipo_documento"]:
            tipo_doc, _ = TipoDocumento.objects.get_or_create(nombre="SIN DOCUMENTO")
            extra_fields["tipo_documento"] = tipo_doc

        if "rol" not in extra_fields or not extra_fields["rol"]:
            rol, _ = Rol.objects.get_or_create(nombre="Admin")
            extra_fields["rol"] = rol

        if "documento" not in extra_fields or not extra_fields["documento"]:
            extra_fields["documento"] = get_random_string(8)  # valor único temporal

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
