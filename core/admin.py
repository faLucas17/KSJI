from django.contrib import admin
from .models import Service, ContactMessage, TeamMember, Testimonial, Appointment

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'date_sent', 'is_read', 'responded']
    list_filter = ['is_read', 'responded', 'date_sent']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['date_sent']
    actions = ['mark_as_read', 'mark_as_responded']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_responded(self, request, queryset):
        queryset.update(responded=True)
    mark_as_responded.short_description = "Marquer comme répondu"

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'position', 'bio']
    list_editable = ['order', 'is_active']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_position', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['client_name', 'content']
    list_editable = ['is_active']

# === GARDEZ CE BLOC (le deuxième avec featured et details) ===
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'featured', 'is_active', 'created_at']
    list_filter = ['is_active', 'featured']
    search_fields = ['title', 'description', 'details']
    list_editable = ['order', 'featured', 'is_active']
    ordering = ['order']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description', 'details', 'icon_class')
        }),
        ('Affichage', {
            'fields': ('order', 'featured', 'is_active')
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_email', 'appointment_type', 
                    'service_needed', 'preferred_date', 'preferred_time', 
                    'status', 'confirmation_sent']
    list_filter = ['status', 'appointment_type', 'service_needed', 
                   'preferred_date', 'confirmation_sent']
    search_fields = ['client_name', 'client_email', 'client_phone', 'description']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_confirmed', 'mark_as_completed']
    
    fieldsets = (
        ('Informations Client', {
            'fields': ('client_name', 'client_email', 'client_phone')
        }),
        ('Détails du Rendez-vous', {
            'fields': ('appointment_type', 'service_needed', 
                      'preferred_date', 'preferred_time', 'duration')
        }),
        ('Informations Complémentaires', {
            'fields': ('description', 'documents', 'notes')
        }),
        ('Statut et Suivi', {
            'fields': ('status', 'confirmation_sent', 'reminder_sent')
        }),
    )
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} rendez-vous marqué(s) comme confirmé(s).")
    mark_as_confirmed.short_description = "Marquer comme confirmé"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} rendez-vous marqué(s) comme terminé(s).")
    mark_as_completed.short_description = "Marquer comme terminé"