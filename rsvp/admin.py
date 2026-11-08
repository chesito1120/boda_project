from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html
from .models import Family, Guest

class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0
    fields = ('full_name', 'has_checked_in', 'check_in_time')
    readonly_fields = ('check_in_time',)

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_tickets', 'confirmed_tickets', 'status', 'is_locked', 'whatsapp_link')
    list_filter = ('status', 'is_locked')
    search_fields = ('name', 'contact_phone')
    inlines = [GuestInline]
    actions = ['unlock_confirmation']

    def whatsapp_link(self, obj):
        if obj.contact_phone:
            url = f"https://wa.me/{obj.contact_phone.replace('+', '').replace(' ', '')}?text=Hola%20{obj.name},%20confirma%20tu%20asistencia%20aquí:%20http://127.0.0.1:8000/invitacion/{obj.id}/"
            return format_html('<a href="{}" target="_blank" style="color: #25D366; font-weight: bold;">WhatsApp</a>', url)
        return "-"
    whatsapp_link.short_description = "Invitación WhatsApp"

    @admin.action(description='Desbloquear confirmación para permitir edición')
    def unlock_confirmation(self, request, queryset):
        queryset.update(is_locked=False)

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'family', 'has_checked_in', 'check_in_time')
    list_filter = ('has_checked_in', 'family')
    search_fields = ('full_name', 'family__name')

