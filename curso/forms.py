from django import forms

class CursoForm(forms.Form):
    codigoprograma = forms.CharField(label="Código del programa", max_length=50)
    nombreprograma = forms.CharField(label="Nombre del programa", max_length=200)
    versionprograma = forms.CharField(label="Versión del programa", max_length=20)
    duracionprograma = forms.CharField(label="Duración (Horas)", max_length=50)
    fechainicio = forms.DateField(label="Fecha de inicio", widget=forms.DateInput(attrs={'type': 'date'}))
    fechafin = forms.DateField(label="Fecha de finalización", widget=forms.DateInput(attrs={'type': 'date'}))
    departamento = forms.CharField(label="Departamento", max_length=100)
    municipio = forms.CharField(label="Municipio", max_length=100)
    direccion = forms.CharField(label="Dirección", max_length=200)
    nombre = forms.CharField(label="Nombre responsable", max_length=200)
    tipodoc = forms.ChoiceField(choices=[("CC", "CC"), ("TI", "TI"), ("CE", "CE")], label="Tipo documento")
    numerodoc = forms.CharField(label="Número de documento", max_length=50)
    correo = forms.EmailField(label="Correo electrónico")
    empresa = forms.CharField(label="Empresa solicitante", max_length=200, required=False)

    # Programa especial (selección única)
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
    programa_especial = forms.ChoiceField(choices=PROGRAMA_CHOICES, label="Programa Especial")

    # Días (selección múltiple)
    DIAS_CHOICES = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Miércoles"),
        ("JUE", "Jueves"),
        ("VIE", "Viernes"),
        ("SAB", "Sábado"),
        ("DOM", "Domingo"),
    ]
    dias = forms.MultipleChoiceField(choices=DIAS_CHOICES, widget=forms.CheckboxSelectMultiple, label="Días de la semana")

    horario = forms.CharField(label="Horario del curso", max_length=100)
    fecha1 = forms.CharField(label="Fechas de ejecución (mes 1)", max_length=200)
    fecha2 = forms.CharField(label="Fechas de ejecución (mes 2)", max_length=200, required=False)
    firma = forms.CharField(label="Firma instructor", required=False)