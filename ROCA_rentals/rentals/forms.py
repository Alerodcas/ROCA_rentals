from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from datetime import date

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['cedula', 'correo', 'password1', 'password2', 'p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'f_nacimiento']
        labels = {
            'cedula': 'Cédula',
            'correo': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
            'p_nombre': 'Nombre',
            's_nombre': 'Segundo Nombre',
            'p_apellido': 'Apellido',
            's_apellido': 'Segundo Apellido',
            'f_nacimiento': 'Fecha de Nacimiento',
        }
        widgets = {
            'f_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']
        if Usuario.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Ya existe un usuario con esta cédula.')
        return cedula

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return correo

    def clean_f_nacimiento(self):
        f_nacimiento = self.cleaned_data['f_nacimiento']
        today = date.today()
        age = today.year - f_nacimiento.year - ((today.month, today.day) < (f_nacimiento.month, f_nacimiento.day))
        if age < 18:
            raise forms.ValidationError('Debes ser mayor de 18 años para registrarte.')
        return f_nacimiento
