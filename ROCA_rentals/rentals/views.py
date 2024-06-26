from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from ROCA_rentals import settings
from .forms import RegistroUsuarioForm
from .forms import UsuarioLoginForm
from .forms import PasswordResetRequestForm
from .models import Usuario
from datetime import date
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login  # Rename to avoid conflict

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Calcular edad
            f_nacimiento = form.cleaned_data['f_nacimiento']
            today = date.today()
            edad = today.year - f_nacimiento.year - ((today.month, today.day) < (f_nacimiento.month, f_nacimiento.day))
            
            # Crear usuario (pero no guardarlo aún)
            usuario = form.save(commit=False)
            usuario.edad = edad
            usuario.is_active = False  # El usuario no está activo hasta que confirme su correo
            
            # Hash the password
            usuario.set_password(form.cleaned_data['password1'])
            
            # Generar token y enviar correo de confirmación
            current_site = get_current_site(request)
            subject = 'Activa tu cuenta'
            message = render_to_string('activation_email.html', {
                'user': usuario,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
                'token': default_token_generator.make_token(usuario),
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [usuario.correo])
            
            # Guardar usuario
            usuario.save()
            
            return render(request, 'registro_pendiente.html')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activation_success.html')
    else:
        return render(request, 'activation_failure.html')
    

def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Usuario.objects.get(correo=email)
            if not user.is_active:
                current_site = get_current_site(request)
                subject = 'Reenvío de Activación de Cuenta'
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.correo])
                messages.success(request, 'Se ha enviado un nuevo enlace de activación a tu correo.')
            else:
                messages.error(request, 'Esta cuenta ya está activada.')
        except Usuario.DoesNotExist:
            messages.error(request, 'No se ha encontrado una cuenta con ese correo electrónico.')
        return redirect('login')
    return render(request, 'resend_activation_email.html')

User = get_user_model()

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(correo=email)
                current_site = get_current_site(request)
                subject = 'Restablecer tu contraseña'
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.correo])
                messages.success(request, 'Se ha enviado un enlace para restablecer tu contraseña a tu correo electrónico.')
                return redirect('password_reset_done')
            except User.DoesNotExist:
                messages.error(request, 'No existe una cuenta con este correo electrónico.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_form.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Tu contraseña ha sido restablecida exitosamente.')
                return redirect('login')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        return render(request, 'password_reset_confirm.html', {'user': user})
    else:
        messages.error(request, 'El enlace de restablecimiento es inválido o ha expirado.')
        return redirect('password_reset_form')

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')


def user_login(request):
    if request.method == 'POST':
        form = UsuarioLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Correct function to log in the user
            messages.success(request, 'Logged in successfully.')
            return redirect('home')  # Redirect to the home page upon successful login
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UsuarioLoginForm(request)

    return render(request, 'login.html', {'form': form})



@login_required
def home(request):
    return render(request, 'home.html')
