from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Service(models.Model):
    """Modèle pour les services de KSJI"""
    title = models.CharField(max_length=100, verbose_name="Titre")
    description = models.TextField(verbose_name="Description courte")
    details = models.TextField(
        verbose_name="Détails complets",
        blank=True,
        help_text="Détails complets du service (liste à puces, etc.)"
    )
    icon_class = models.CharField(
        max_length=50, 
        default="fas fa-balance-scale",
        verbose_name="Classe d'icône"
    )
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    featured = models.BooleanField(default=False, verbose_name="En vedette (page d'accueil)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order']

    def __str__(self):
        return self.title
    

class ContactMessage(models.Model):
    """Modèle pour les messages de contact"""
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    
    # CORRECTION ICI : Meilleur regex pour Sénégal
    phone_regex = RegexValidator(
        regex=r'^\+?221?\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$',
        message="Format: +221 77 123 45 67 ou 771234567"
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=20, 
        blank=True,
        verbose_name="Téléphone"
    )
    
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    date_sent = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    responded = models.BooleanField(default=False, verbose_name="Répondu")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_sent']

    def __str__(self):
        return f"{self.subject} - {self.name}"

class TeamMember(models.Model):
    """Modèle pour les membres de l'équipe"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    position = models.CharField(max_length=100, verbose_name="Poste")
    bio = models.TextField(verbose_name="Biographie", blank=True)
    photo = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.position}"

class Testimonial(models.Model):
    """Modèle pour les témoignages"""
    client_name = models.CharField(max_length=100, verbose_name="Nom du client")
    client_position = models.CharField(max_length=100, blank=True, verbose_name="Poste du client")
    content = models.TextField(verbose_name="Témoignage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Témoignage de {self.client_name}"
    
class Appointment(models.Model):
    """Modèle pour les rendez-vous"""
    APPOINTMENT_TYPES = [
        ('online', 'Consultation en ligne (Visio)'),
        ('in_person', 'Consultation en présentiel'),
        ('phone', 'Consultation téléphonique'),
    ]
    
    SERVICE_CHOICES = [
        ('droit_famille', 'Droit de la famille'),
        ('droit_affaires', 'Droit des affaires'),
        ('droit_immobilier', 'Droit immobilier'),
        ('droit_successoral', 'Droit successoral'),
        ('droit_travail', 'Droit du travail'),
        ('autre', 'Autre'),
    ]
    
    # Informations client
    client_name = models.CharField(max_length=100, verbose_name="Nom complet")
    client_email = models.EmailField(verbose_name="Email")
    client_phone = models.CharField(max_length=20, verbose_name="Téléphone")
    
    # Détails du rendez-vous
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPES,
        default='online',
        verbose_name="Type de consultation"
    )
    
    service_needed = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        verbose_name="Service demandé"
    )
    
    preferred_date = models.DateField(verbose_name="Date souhaitée")
    preferred_time = models.TimeField(verbose_name="Heure souhaitée")
    
    duration = models.IntegerField(
        default=60,
        validators=[MinValueValidator(30), MaxValueValidator(180)],
        verbose_name="Durée estimée (minutes)",
        help_text="Entre 30 et 180 minutes"
    )
    
    # Informations supplémentaires
    description = models.TextField(
        verbose_name="Description de votre situation",
        help_text="Décrivez brièvement votre situation pour préparer la consultation"
    )
    
    # Documents (optionnel)
    documents = models.FileField(
        upload_to='appointment_docs/',
        blank=True,
        null=True,
        verbose_name="Documents joints"
    )
    
    # Statut
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    
    # Suivi
    confirmation_sent = models.BooleanField(default=False, verbose_name="Email de confirmation envoyé")
    reminder_sent = models.BooleanField(default=False, verbose_name="Rappel envoyé")
    notes = models.TextField(blank=True, verbose_name="Notes internes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['preferred_date', 'preferred_time']
    
    def __str__(self):
        return f"{self.client_name} - {self.get_appointment_type_display()} - {self.preferred_date}"
    
    def get_full_type_display(self):
        return f"{self.get_appointment_type_display()} ({self.get_service_needed_display()})"