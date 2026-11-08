from django.urls import path
from . import views

urlpatterns = [
    path('novios/', views.couples_dashboard, name='couples_dashboard'),
    path('novios/editar/<uuid:family_id>/', views.edit_family, name='edit_family'),
    path('novios/eliminar/<uuid:family_id>/', views.delete_family, name='delete_family'),
    path('invitacion/<uuid:token>/', views.invitation_view, name='invitation_view'),
    path('invitacion/<uuid:token>/qr/', views.qr_code_view, name='qr_code_view'),
    path('staff/checkin/', views.checkin_dashboard, name='checkin_dashboard'),
    path('staff/checkin/toggle/<int:guest_id>/', views.toggle_guest_checkin, name='toggle_guest_checkin'),
]