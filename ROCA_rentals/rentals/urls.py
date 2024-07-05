from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend_activation_email/', views.resend_activation_email, name='resend_activation_email'),

    path('home/', views.home, name='home'),  # Ensure this is correct
    path('alquileres/', views.alquileres, name='alquileres'),

    path('add_tipo/', views.add_tipo, name='add_tipo'),
    path('add_arrendamiento/', views.add_arrendamiento, name='add_arrendamiento'),
    path('alquileres/<int:arrendamiento_id>/deudas/', views.deudas, name='deudas'),
    path('edit_tipo/', views.edit_tipo, name='edit_tipo'),
    path('alquileres/edit/<int:arrendamiento_id>/', views.edit_arrendamiento, name='edit_arrendamiento'),





    # Password reset URLs
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]

