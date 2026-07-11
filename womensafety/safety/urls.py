from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('safety/', RedirectView.as_view(pattern_name='sos', permanent=False), name='safety'),
    path('safety/sos/', views.sos_view, name='sos'),
    path('safety/sos/trigger/', views.sos_trigger_view, name='sos_trigger'),
    path('safety/contacts/', views.emergency_contacts_view, name='emergency_contacts'),
    path('safety/contacts/add/', views.add_contact_view, name='add_contact'),
    path('safety/contacts/<int:pk>/delete/', views.delete_contact_view, name='delete_contact'),
    path('api/contacts/<int:pk>/delete/', views.delete_contact_view),
    path('safety/live-location/', views.live_location_view, name='live_location'),
    path('safety/live-location/update/', views.update_location_api, name='update_location'),
    path('safety/safe-route/', views.safe_route_view, name='safe_route'),
]
