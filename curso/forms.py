from django import forms
from .models import Usuario, Programa, Departamento, Municipio, Aspirante, Area, Curso 
from django.core.validators import FileExtensionValidator

class InicioSesionForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su correo"
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su contraseña"
        })
    )

class UsuarioCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su contraseña"
        }),
        label="Contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme su contraseña"
        }),
        label="Confirmar contraseña"
    )
    firma_digital = forms.ImageField(
        required=False,
        label="Firma Digital",
        help_text="Formatos permitidos: PNG, JPG. Tamaño máximo recomendado: 500x200px",
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": "image/png, image/jpeg"
        })
    )

    class Meta:
        model = Usuario
        fields = [
            "first_name",
            "last_name",
            "email",
            "documento",
            "tipo_documento",
            "password",
            "confirm_password",
            "rol",
            "firma_digital",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su nombre"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su apellido"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su correo"
            }),
            "documento": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de documento"
            }),
            "tipo_documento": forms.Select(attrs={
                "class": "form-select"
            }),
            "rol": forms.Select(attrs={
                "class": "form-select"
            }),
            "firma": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        firma_digital = cleaned_data.get("firma_digital")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
        # Validar tamaño de la imagen si se proporciona
        if firma_digital:
            try:
                from django.core.files.images import get_image_dimensions
                width, height = get_image_dimensions(firma_digital)
                if width > 500 or height > 200:
                    raise forms.ValidationError("La imagen de firma no debe exceder 500x200 píxeles")
            except Exception:
                raise forms.ValidationError("Error al procesar la imagen de firma")
        
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario

class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nueva contraseña"
        }),
        required=False,
        label="Nueva contraseña",
        help_text="Deja en blanco si no deseas cambiarla."
    )
    firma_digital = forms.ImageField(
        required=False,
        label="Firma Digital",
        help_text="Formatos permitidos: PNG, JPG. Tamaño máximo recomendado: 500x200px",
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": "image/png, image/jpeg"
        })
    )

    class Meta:
        model = Usuario
        fields = [
            "first_name",
            "last_name",
            "email",
            "documento",
            "tipo_documento",
            "rol",
            "firma_digital",
            "password",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su nombre"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su apellido"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su correo"
            }),
            "documento": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "tipo_documento": forms.Select(attrs={
                "class": "form-select"
            }),
            "rol": forms.Select(attrs={
                "class": "form-select"
            }),
            "firma": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documento'].disabled = True    

    def clean(self):
        cleaned_data = super().clean()
        firma_digital = cleaned_data.get("firma_digital")

        # Validar tamaño de la imagen si se proporciona
        if firma_digital:
            try:
                from django.core.files.images import get_image_dimensions
                width, height = get_image_dimensions(firma_digital)
                if width > 500 or height > 200:
                    raise forms.ValidationError("La imagen de firma no debe exceder 500x200 píxeles")
            except Exception:
                raise forms.ValidationError("Error al procesar la imagen de firma")
        
        return cleaned_data    

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:  # solo cambiar si se digitó
            usuario.set_password(password)
        if commit:
            usuario.save()
        return usuario

class CursoForm(forms.Form):
    
    # ---------- AREA ----------
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        required=False,
        label="Área",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    duracion_filtro = forms.ChoiceField(
        choices=[],
        required=False,
        label="Duración (Horas)",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Curso
        fields = [
            "nombreprograma", "codigoprograma", "versionprograma", "duracionprograma",
            "fechainicio", "fechafin", "dias", "horario_inicio", "horario_fin",
            # … demás campos
        ]
    
    # ---------- PROGRAMA ----------
    nombreprograma = forms.ModelChoiceField(
        queryset=Programa.objects.all(),
        label="Nombre del programa",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    codigoprograma = forms.CharField(
        label="Código del programa",
        max_length=50,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"})
    )
    versionprograma = forms.CharField(
        label="Versión del programa",
        max_length=20,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"})
    )
    duracionprograma = forms.CharField(
        label="Duración (Horas)",
        max_length=50,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"})
    )

    # ---------- FECHAS ----------
    fechainicio = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"})
    )
    fechafin = forms.DateField(
        label="Fecha de finalización",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control", "readonly": "readonly"})
    )

    # ---------- UBICACIÓN ----------
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        label="Departamento",
        empty_label="Seleccione un departamento",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        label="Municipio",
        empty_label="Seleccione un municipio",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    direccion = forms.CharField(label="Dirección", max_length=200,
                                widget=forms.TextInput(attrs={"class": "form-control"}))

    # ---------- RESPONSABLE (usuario logueado) ----------
    nombre = forms.CharField(label="Nombre responsable", max_length=200, disabled=True, required=False,
                             widget=forms.TextInput(attrs={"class": "form-control"}))
    tipodoc = forms.CharField(label="Tipo documento", disabled=True, required=False,
                              widget=forms.TextInput(attrs={"class": "form-control"}))
    numerodoc = forms.CharField(label="Número de documento", max_length=50, disabled=True, required=False,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    correo = forms.EmailField(label="Correo electrónico", disabled=True, required=False,
                              widget=forms.EmailInput(attrs={"class": "form-control"}))

    # ---------- EMPRESA ----------
    empresa = forms.CharField(label="Empresa solicitante", max_length=200, required=False,
                              widget=forms.TextInput(attrs={"class": "form-control", "id": "id_empresa"}))
    carta_empresa = forms.FileField(label="Carta de empresa", required=False,
                                    widget=forms.ClearableFileInput(attrs={"class": "form-control"}))

    # ---------- PROGRAMAS ESPECIALES ----------
    PROGRAMA_CHOICES = [
        ("SENA EMPREDE RURAL", "SENA EMPREDE RURAL"),
        ("SENA EMPRENDE RURAL- POST CONFLICTO (ETCR)", "SENA EMPRENDE RURAL- POST CONFLICTO (ETCR)"),
        ("AULAS ABIERTAS", "AULAS ABIERTAS"),
        ("PROGRAMA DE EMPRENDIMIENTO", "PROGRAMA DE EMPRENDIMIENTO"),
        ("CATEDRA VIRTUAL DE PRODUCTIVIDAD", "CÁTEDRA VIRTUAL DE PRODUCTIVIDAD"),
        ("PROGRAMA DE BILINGUISMO", "PROGRAMA DE BILINGÜISMO"),
        ("JOVENES RURALES SIN ALIANZAS", "JÓVENES RURALES SIN ALIANZAS"),
        ("CAPACIDAD DE GESTION DE EXPORTACIONES", "CAPACIDAD DE GESTIÓN DE EXPORTACIONES"),
        ("LEOS – LABORATORIOS EXPERIMENTALES", "LEOS – LABORATORIOS EXPERIMENTALES"),
        ("AULA MOVIL", "AULA MÓVIL"),
        ("AMBIENTES VIRTUALES DE APRENDIZAJE", "AMBIENTES VIRTUALES DE APRENDIZAJE"),
        ("CATEDRA VIRTUAL DE PENSAMIENTO EMPRESARIAL", "CÁTEDRA VIRTUAL DE PENSAMIENTO EMPRESARIAL"),
        ("PROGRAMA JOVENES EN ACCION", "PROGRAMA JÓVENES EN ACCIÓN"),
        ("ALIANZAS ESTRATEGICAS", "ALIANZAS ESTRATÉGICAS"),
        ("ALTA GERENCIA", "ALTA GERENCIA"),
    ]
    programa_especial = forms.ChoiceField(choices=PROGRAMA_CHOICES, label="Programa Especial", required=False)

    # ---------- HORARIOS ----------
    DIAS_CHOICES = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Miércoles"),
        ("JUE", "Jueves"),
        ("VIE", "Viernes"),
        ("SAB", "Sábado"),
        ("DOM", "Domingo"),
    ]
    dias = forms.MultipleChoiceField(
        choices=DIAS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Días de la semana"
    )

    TIPO_HORARIO_CHOICES = [
        ("general", "Horario general"),
        ("individual", "Horario por día"),
    ]
    tipo_horario = forms.ChoiceField(
        choices=TIPO_HORARIO_CHOICES,
        widget=forms.RadioSelect,
        initial="general",
        label="Tipo de horario"
    )

    horario_inicio = forms.TimeField(
        label="Hora inicio",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'id_horario_inicio'})
    )
    horario_fin = forms.TimeField(
        label="Hora fin",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'id_horario_fin'})
    )

    # ---------- SALIDA DE FECHAS ----------
    fecha1 = forms.CharField(
        label="Fechas de ejecución (mes 1)",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"class": "form-control", "readonly": "readonly"})
    )
    fecha2 = forms.CharField(
        label="Fechas de ejecución (mes 2)",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"class": "form-control", "readonly": "readonly"})
    )

    # ---------- FIRMA ----------
    firma = forms.FileField(
            label="Firma instructor",
            required=False,
            widget=forms.ClearableFileInput(attrs={"class": "form-control d-none hidden "})  # oculto en el form
        )
    # ---------- INIT ----------
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

        
        self.fields["duracion_filtro"].choices = [("", "---------")] + [
            (d, d) for d in Programa.objects.values_list("duracion", flat=True).distinct() if d
        ]

        # Manejo dinámico de municipios
        if "departamento" in self.data:
            try:
                departamento_id = int(self.data.get("departamento"))
                self.fields["municipio"].queryset = Municipio.objects.filter(departamento_id=departamento_id)
            except (ValueError, TypeError):
                self.fields["municipio"].queryset = Municipio.objects.none()
        elif self.initial.get("departamento"):
            self.fields["municipio"].queryset = Municipio.objects.filter(departamento=self.initial["departamento"])

        # Prellenar datos del usuario autenticado
        if usuario:
            self.fields["nombre"].initial = f"{usuario.first_name} {usuario.last_name}".strip()
            if getattr(usuario, "tipo_documento", None):
                self.fields["tipodoc"].initial = getattr(usuario.tipo_documento, "nombre", "")
            self.fields["numerodoc"].initial = getattr(usuario, "documento", "")
            self.fields["correo"].initial = usuario.email
            if usuario.firma_digital:
                self.fields["firma"].initial = usuario.firma_digital

class AspiranteForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre completo",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    documento = forms.CharField(
        label="Número de documento",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    telefono = forms.CharField(
        label="Teléfono de contacto",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

class AspiranteForm(forms.ModelForm):
    class Meta:
        model = Aspirante
        fields = ["nombre", "documento", "correo", "telefono", "poblacion", "tipo_documento", "archivo_documento"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "documento": forms.TextInput(attrs={"class": "form-control", "placeholder": "Documento"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Teléfono"}),
            "poblacion": forms.Select(attrs={"class": "form-control"}),
            "tipo_documento": forms.Select(attrs={"class": "form-control"}),
            "archivo_documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }