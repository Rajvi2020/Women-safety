from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import FAQ, Resource

@login_required
def resources_view(request):
    category = request.GET.get('category', '').strip()
    resources = Resource.objects.all()
    if category:
        resources = resources.filter(category=category)
        
    return render(request, 'resources/resources.html', {
        'faqs': FAQ.objects.all(),
        'resources': resources,
    })
