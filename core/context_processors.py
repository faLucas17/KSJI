from .models import Service

def services_context(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    return {'all_services': services}