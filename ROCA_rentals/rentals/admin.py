from django.contrib import admin
from .models import Tipo, Usuario, TelefonoUsuario, Arrendamiento, Inquilino, TelefonoInquilino, Pago, Contribucion

admin.site.register(Tipo)
admin.site.register(Usuario)
admin.site.register(TelefonoUsuario)
admin.site.register(Arrendamiento)
admin.site.register(Inquilino)
admin.site.register(TelefonoInquilino)
admin.site.register(Pago)
admin.site.register(Contribucion)
