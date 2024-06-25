from django.db import models
from django.contrib.auth.models import AbstractUser


class Tipo(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion
    
class Usuario(AbstractUser):
    cedula = models.CharField(primary_key=True, max_length=50)
    correo = models.EmailField(unique=True)
    p_nombre = models.CharField(max_length=50)
    s_nombre = models.CharField(max_length=50, null=True, blank=True)
    p_apellido = models.CharField(max_length=50)
    s_apellido = models.CharField(max_length=50, null=True, blank=True)
    f_nacimiento = models.DateField()
    edad = models.IntegerField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.p_nombre} {self.p_apellido}"

    # Define the related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',  # Specify a different related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_set',  # Specify a different related name
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='usuario',
    )

    
class TelefonoUsuario(models.Model):
    cedula = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)  

    class Meta:
        unique_together = ('cedula', 'telefono')


class Arrendamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nise = models.CharField(max_length=50)  
    med_agua = models.CharField(max_length=50)  
    num_casa = models.CharField(max_length=50)
    alquiler = models.DecimalField(max_digits=10, decimal_places=2)  # Kept decimal places as 2
    ubicacion = models.TextField()
    ced_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Arrendamiento {self.id} - {self.num_casa}"

    
class Inquilino(models.Model):
    id = models.AutoField(primary_key=True)
    deuda = models.IntegerField()
    apodo = models.CharField(max_length=50, null=True)
    p_nombre = models.CharField(max_length=50)
    s_nombre = models.CharField(max_length=50, null=True, blank=True)
    p_apellido = models.CharField(max_length=50)
    s_apellido = models.CharField(max_length=50, null=True, blank=True)
    f_nacimiento = models.DateField()
    edad = models.IntegerField()
    id_casa = models.ForeignKey(Arrendamiento, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.p_nombre


class TelefonoInquilino(models.Model):
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)  # Changed to CharField to match the ER diagram

    class Meta:
        unique_together = ('inquilino', 'telefono')

class Pago(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, null = True)
    fecha = models.DateField()
    luz = models.DecimalField(max_digits=10, decimal_places=2)
    agua = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    restante = models.DecimalField(max_digits=10, decimal_places=2)
    completado = models.BooleanField()
    id_inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pago {self.id} - {self.fecha}"

class Contribucion(models.Model):
    id_pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('id_pago', 'fecha')




