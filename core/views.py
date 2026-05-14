from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView
from .models import Service, TeamMember, Testimonial
from .forms import ContactForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Appointment
from .forms import AppointmentForm


class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # SEULEMENT les services "featured" et actifs
        context['featured_services'] = Service.objects.filter(
            is_active=True, 
            featured=True
        ).order_by('order')[:4]  # Maximum 4 services
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:3] if hasattr(Testimonial, 'objects') else []
        return context

def services_view(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    return render(request, 'services.html', {'services': services})

def about_view(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    return render(request, 'about.html', {'team_members': team_members})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        print("POST data:", request.POST)  # DEBUG
        print("Form is valid?", form.is_valid())  # DEBUG
        
        if form.is_valid():
            contact_message = form.save()
            print("Message saved:", contact_message.id)  # DEBUG
            
            # Email 1 : À vous (texte simple)
            subject_to_you = f"Nouveau message KSJI: {contact_message.subject}"
            message_to_you = f"""Nouveau message reçu sur KSJI:

Nom: {contact_message.name}
Email: {contact_message.email}
Téléphone: {contact_message.phone if contact_message.phone else 'Non fourni'}
Sujet: {contact_message.subject}

Message:
{contact_message.message}

---
Date: {contact_message.date_sent}
"""
            
            # Email 2 : Au client (HTML professionnel)
            subject_to_client = f"KSJI - Accusé de réception: {contact_message.subject}"
            
            # Rendre le template HTML
            html_message_client = render_to_string('emails/contact_confirmation_client.html', {
                'contact_message': contact_message
            })
            
            # Version texte simple pour les clients qui ne supportent pas HTML
            plain_message_client = f"""Bonjour {contact_message.name},

Nous vous confirmons la bonne réception de votre message concernant : 
"{contact_message.subject}"

Votre message :
{contact_message.message}

Notre équipe prendra contact avec vous dans les plus brefs délais (généralement sous 24h).

Pour rappel, nos coordonnées :
📧 Email : contactksji@gmail.com
📞 Téléphone : +221 77 200 00 00

Cordialement,
Me Fatou FALL
Avocate - Cabinet KSJI
"""
            
            try:
                print("Attempting to send email...")  # DEBUG
                
                # Envoyer à vous (texte simple)
                send_mail(
                    subject_to_you,
                    message_to_you,
                    settings.DEFAULT_FROM_EMAIL,
                    ['contactksji@gmail.com'],  # TON EMAIL
                    fail_silently=False,
                )
                print("Email to admin sent")  # DEBUG
                
                # Envoyer au client (HTML + texte)
                send_mail(
                    subject_to_client,
                    plain_message_client,  # Version texte
                    settings.DEFAULT_FROM_EMAIL,
                    [contact_message.email],  # Email du client
                    html_message=html_message_client,  # Version HTML
                    fail_silently=False,
                )
                print("Email to client sent")  # DEBUG
                
                # REDIRECTION vers la page de succès au lieu de rester sur contact
                return redirect('contact_success')
                
            except Exception as e:
                print("Email error:", str(e))  # DEBUG
                messages.error(request, f"⚠️ Erreur technique: {str(e)}")
                return render(request, 'contact.html', {'form': form})
        else:
            # Affiche les erreurs spécifiques
            print("Form errors:", form.errors)  # DEBUG
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:  # GET request
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def contact_success(request):
    """Page de succès après envoi du formulaire de contact"""
    return render(request, 'contact_success.html')

def legal_view(request):
    return render(request, 'legal.html')

class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment.html'
    success_url = reverse_lazy('appointment_success')
    
    def form_valid(self, form):
        # Sauvegarder le rendez-vous
        appointment = form.save()
        
        # Email au client
        subject_client = f"KSJI - Confirmation de votre demande de rendez-vous"
        message_client = f"""Bonjour {appointment.client_name},

Nous confirmons la réception de votre demande de rendez-vous pour le {appointment.preferred_date} à {appointment.preferred_time}.

Type : {appointment.get_appointment_type_display()}
Service : {appointment.get_service_needed_display()}
Durée : {appointment.duration} minutes

Votre message : {appointment.description}

Nous vous contacterons dans les prochaines 24h pour finaliser les détails.

Cordialement,
L'équipe KSJI
Email : ksji.contact@gmail.com
Téléphone : +221 77 200 00 00
"""
        
        # Email à l'admin
        subject_admin = f"KSJI - Nouvelle demande de rendez-vous de {appointment.client_name}"
        message_admin = f"""NOUVELLE DEMANDE DE RENDEZ-VOUS :

👤 Client : {appointment.client_name}
📧 Email : {appointment.client_email}
📞 Téléphone : {appointment.client_phone}

📅 Date : {appointment.preferred_date}
⏰ Heure : {appointment.preferred_time}
🕐 Durée : {appointment.duration} minutes

🏛️ Type : {appointment.get_appointment_type_display()}
⚖️ Service : {appointment.get_service_needed_display()}

📝 Description :
{appointment.description}

---
⚠️ ACTION REQUISE : Contacter le client pour confirmer le rendez-vous.
"""
        
        try:
            # Envoyer au client
            send_mail(
                subject_client,
                message_client,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.client_email],
                fail_silently=False,
            )
            
            # Envoyer à l'admin
            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                ['contactksji@gmail.com'],
                fail_silently=False,
            )
            
            appointment.confirmation_sent = True
            appointment.save()
            
        except Exception as e:
            # Même en cas d'erreur email, on sauvegarde le rendez-vous
            messages.warning(self.request, f"Rendez-vous enregistré mais erreur d'email: {str(e)}")
        
        return super().form_valid(form)

def appointment_success(request):
    return render(request, 'appointment_success.html')