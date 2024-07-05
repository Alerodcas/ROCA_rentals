from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from ROCA_rentals import settings
from .forms import *
from .models import *
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
    buttons = [
        {'name': 'Alquileres', 'icon': 'images/icons/icons8_alquileres.png', 'dir': 'alquileres'},
        {'name': 'Inquilinos', 'icon': 'images/icons/icons8_inquilinos.png', 'dir': 'alquileres'},
        {'name': 'Imprimir Recibos', 'icon': 'images/icons/icons8_recibos.png', 'dir': 'alquileres'},
        {'name': 'Ir a Cobrar', 'icon': 'images/icons/icons8_cobrar.png', 'dir': 'alquileres'},
        {'name': 'Ver Deudas', 'icon': 'images/icons/icons8_deuda.png', 'dir': 'alquileres'},
        {'name': 'Reportes Mensuales', 'icon': 'images/icons/icons8_reportes.png', 'dir': 'alquileres'},
        {'name': 'Enviar Mensajes', 'icon': 'images/icons/icons8_message2.png', 'dir': 'alquileres'}
    ]
    
    return render(request, 'home.html', {'buttons': buttons})

@login_required
def alquileres(request):
    tipos = Tipo.objects.all()
    for tipo in tipos:
        tipo.arrendamientos = Arrendamiento.objects.filter(tipo=tipo, ced_usuario=request.user)
        for arrendamiento in tipo.arrendamientos:
            inquilino = Inquilino.objects.filter(id_casa=arrendamiento).first()
            arrendamiento.inquilino = inquilino
            if inquilino:
                pagos_no_pagados = Pago.objects.filter(id_inquilino=inquilino, completado=False)
                arrendamiento.deuda = sum(pago.restante for pago in pagos_no_pagados)
            else:
                arrendamiento.deuda = 0

    if request.method == 'POST':
        if 'tipo_form' in request.POST:
            tipo_form = TipoForm(request.POST)
            if tipo_form.is_valid():
                tipo_form.save()
                return redirect('alquileres')
        elif 'arrendamiento_form' in request.POST:
            arrendamiento_form = ArrendamientoForm(request.POST)
            if arrendamiento_form.is_valid():
                arrendamiento = arrendamiento_form.save(commit=False)
                arrendamiento.ced_usuario = request.user
                arrendamiento.save()
                return redirect('alquileres')
    else:
        tipo_form = TipoForm()
        arrendamiento_form = ArrendamientoForm()

    return render(request, 'alquileres.html', {
        'tipos': tipos,
        'tipo_form': tipo_form,
        'arrendamiento_form': arrendamiento_form,
    })


def edit_tipo(request):
    if request.method == 'POST':
        tipo_id = request.POST.get('tipo')

        if tipo_id == "todos":
            arrendamientos = Arrendamiento.objects.all()
        else:
            tipo = get_object_or_404(Tipo, id=tipo_id)
            arrendamientos = tipo.arrendamiento_set.all()

        if 'increase_form' in request.POST:
            increase_amount = int(request.POST.get('increase_amount', 0))
            for arrendamiento in arrendamientos:
                arrendamiento.alquiler += increase_amount
                arrendamiento.save()
            messages.success(request, 'Alquileres aumentados exitosamente.')

        elif 'decrease_form' in request.POST:
            decrease_amount = int(request.POST.get('decrease_amount', 0))
            for arrendamiento in arrendamientos:
                arrendamiento.alquiler -= decrease_amount
                arrendamiento.save()
            messages.success(request, 'Alquileres disminuidos exitosamente.')

        elif 'delete_form' in request.POST and tipo_id != "todos":
            tipo = get_object_or_404(Tipo, id=tipo_id)
            tipo_description = tipo.descripcion  # Retrieve the tipo description
            tipo.delete()
            messages.success(request, f'Tipo "{tipo_description}" y sus arrendamientos eliminados exitosamente.')
            return redirect('alquileres')  # Ensure to redirect after setting message

    return redirect('alquileres')

def add_tipo(request):
    if request.method == 'POST':
        form = TipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('alquileres')
    else:
        form = TipoForm()
    return render(request, 'add_tipo.html', {'form': form})

def add_arrendamiento(request):
    if request.method == 'POST':
        form = ArrendamientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('alquileres')
    else:
        form = ArrendamientoForm()
    return render(request, 'add_arrendamiento.html', {'form': form})

def deudas(request, arrendamiento_id):
    arrendamiento = get_object_or_404(Arrendamiento, pk=arrendamiento_id)
    inquilino = arrendamiento.inquilino_set.first()
    if inquilino:
        deudas = Pago.objects.filter(id_inquilino=inquilino, completado=False)
    else:
        deudas = []
    return render(request, 'deudas.html', {'arrendamiento': arrendamiento, 'deudas': deudas})

def edit_arrendamiento(request, arrendamiento_id):
    arrendamiento = get_object_or_404(Arrendamiento, pk=arrendamiento_id)
    inquilinos = Inquilino.objects.all()

    if request.method == 'POST':
        arrendamiento.nombre = request.POST.get('nombre')
        arrendamiento.alquiler = request.POST.get('alquiler')
        arrendamiento.nise = request.POST.get('nise')
        arrendamiento.med_agua = request.POST.get('med_agua')
        arrendamiento.ubicacion = request.POST.get('ubicacion')

        inquilino_id = request.POST.get('inquilino')
        if inquilino_id:
            arrendamiento.inquilino = Inquilino.objects.get(pk=inquilino_id)
        else:
            arrendamiento.inquilino = None

        arrendamiento.save()
        messages.success(request, 'Arrendamiento actualizado correctamente')
        return redirect('alquileres')

    return render(request, 'edit_arrendamiento.html', {'arrendamiento': arrendamiento, 'inquilinos': inquilinos})
