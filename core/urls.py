from django.urls import path
from . import views
from .views import AppointmentCreateView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.services_view, name='services'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    path('legal/', views.legal_view, name='legal'),
     # Rendez-vous
    path('appointment/', AppointmentCreateView.as_view(), name='appointment'),
    path('appointment/success/', views.appointment_success, name='appointment_success'),
]