from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from ROCA_rentals import settings
from .forms import RegistroUsuarioForm
from .models import Usuario
from datetime import date
from django.utils.http import urlsafe_base64_decode

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

def login(request):
    return render(request, 'Login.html')
