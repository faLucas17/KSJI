from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from django.utils import timezone
from datetime import timedelta, datetime, time
from .models import ContactMessage, Appointment

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+221 77 XXX XX XX'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de votre message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message...'
            }),
        }
        labels = {
            'name': 'Nom complet',
            'email': 'Adresse email',
            'phone': 'Numéro de téléphone (optionnel)',
            'subject': 'Sujet',
            'message': 'Message',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # DÉSACTIVE la validation regex pour le champ phone dans le formulaire
        if 'phone' in self.fields:
            self.fields['phone'].validators = []
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'contact-form'
        self.helper.add_input(Submit('submit', 'Envoyer', css_class='btn-primary'))

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'client_name', 'client_email', 'client_phone',
            'appointment_type', 'service_needed',
            'preferred_date', 'preferred_time', 'duration',
            'description', 'documents'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+221 77 123 45 67'
            }),
            'appointment_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'appointment-type'
            }),
            'service_needed': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'preferred-date',
                'min': timezone.now().strftime('%Y-%m-%d')
            }),
            'preferred_time': forms.Select(attrs={
                'class': 'form-control',
                'id': 'preferred-time'
            }),
            'duration': forms.Select(attrs={
                'class': 'form-control',
                'id': 'duration'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez brièvement votre situation...'
            }),
            'documents': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
        }
        labels = {
            'client_name': 'Nom complet*',
            'client_email': 'Email*',
            'client_phone': 'Téléphone*',
            'appointment_type': 'Type de consultation*',
            'service_needed': 'Service demandé*',
            'preferred_date': 'Date souhaitée*',
            'preferred_time': 'Heure souhaitée*',
            'duration': 'Durée estimée*',
            'description': 'Description de votre situation*',
            'documents': 'Documents joints (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Générer les heures disponibles (9h-18h)
        time_choices = []
        for hour in range(9, 18):
            for minute in ['00', '30']:
                if hour == 17 and minute == '30':  # Dernière heure 17:30
                    break
                time_str = f"{hour:02d}:{minute}"
                time_display = f"{hour:02d}h{minute}"
                time_choices.append((time_str, time_display))
        
        self.fields['preferred_time'].widget.choices = [('', 'Choisissez une heure')] + time_choices
        
        # Durées disponibles
        self.fields['duration'].widget.choices = [
            (30, '30 minutes'),
            (60, '1 heure'),
            (90, '1 heure 30'),
            (120, '2 heures'),
        ]
    
    def clean_preferred_date(self):
        date = self.cleaned_data['preferred_date']
        today = timezone.now().date()
        
        # Pas de rendez-vous le jour même (trop court)
        if date == today:
            raise forms.ValidationError("Les rendez-vous doivent être pris au moins 24h à l'avance.")
        
        # Pas de rendez-vous plus de 3 mois à l'avance
        if date > today + timedelta(days=90):
            raise forms.ValidationError("Les rendez-vous ne peuvent pas être pris plus de 3 mois à l'avance.")
        
        # Pas de rendez-vous le dimanche
        if date.weekday() == 6:  # Dimanche
            raise forms.ValidationError("Nous ne travaillons pas le dimanche.")
        
        # Pour samedi : seulement le matin
        if date.weekday() == 5:  # Samedi
            # On vérifiera l'heure dans clean_preferred_time
            pass
        
        return date
    
    def clean_preferred_time(self):
        time_obj = self.cleaned_data['preferred_time']
        date = self.cleaned_data.get('preferred_date')
        
        if not time_obj:
            raise forms.ValidationError("Veuillez sélectionner une heure.")
        
        # Vérifier les heures de travail (9h-18h)
        if time_obj < time(9, 0) or time_obj >= time(18, 0):
            raise forms.ValidationError("Les consultations ont lieu entre 9h et 18h.")
        
        # Pour samedi : seulement jusqu'à 13h
        if date and date.weekday() == 5:  # Samedi
            if time_obj >= time(13, 0):
                raise forms.ValidationError("Les consultations le samedi ont lieu uniquement le matin (9h-13h).")
        
        return time_obj
    
    def clean(self):
        cleaned_data = super().clean()
        appointment_type = cleaned_data.get('appointment_type')
        preferred_date = cleaned_data.get('preferred_date')
        preferred_time = cleaned_data.get('preferred_time')
        
        # Pour les consultations en présentiel : pas après 17h
        if appointment_type == 'in_person' and preferred_time:
            if preferred_time >= time(17, 0):
                raise forms.ValidationError({
                    'preferred_time': "Les consultations en présentiel se terminent à 17h."
                })
        
        return cleaned_data