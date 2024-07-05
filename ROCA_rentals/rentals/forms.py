from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from datetime import date
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['cedula', 'correo', 'password1', 'password2', 'p_nombre', 's_nombre', 'p_apellido', 's_apellido', 'f_nacimiento']
        labels = {
            'cedula': 'Cédula',
            'correo': 'Correo electrónico',
            'p_nombre': 'Nombre',
            's_nombre': 'Segundo Nombre',
            'p_apellido': 'Apellido',
            's_apellido': 'Segundo Apellido',
            'f_nacimiento': 'Fecha de Nacimiento',
        }
        widgets = {
            'f_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'

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

    
Usuario = get_user_model()

class UsuarioLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError('Esta cuenta no ha sido activada. Por favor, revisa tu correo para activarla.')

    def get_user(self):
        return self.user_cache if self.is_valid() else None



class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')

class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['descripcion']
        labels = {
            'descripcion': 'Nombre',
        }

class ArrendamientoForm(forms.ModelForm):
    class Meta:
        model = Arrendamiento
        fields = ['nombre', 'nise', 'med_agua', 'alquiler', 'ubicacion', 'tipo']
        labels = {
            'med_agua': 'Medidor de agua',
        }
        widgets = {
            'alquiler': forms.TextInput(attrs={'placeholder': '₡'}),
        }

        ubicacion = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['descripcion']



