from django.db import models
import uuid
from django.db import models
from django.core.exceptions import ValidationError

class Family(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmado'),
        ('DECLINED', 'Declinado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nombre de la Familia / Grupo', max_length=150)
    contact_phone = models.CharField('Teléfono / WhatsApp', max_length=20, blank=True)
    contact_email = models.EmailField('Correo Electrónico', blank=True)
    
    assigned_tickets = models.PositiveIntegerField('Boletos Asignados', default=1)
    confirmed_tickets = models.PositiveIntegerField('Boletos Confirmados', default=0)
    
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='PENDING')
    is_locked = models.BooleanField('Confirmación Bloqueada', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.confirmed_tickets > self.assigned_tickets:
            raise ValidationError('Los boletos confirmados no pueden exceder los asignados.')

    def __str__(self):
        return f"{self.name} ({self.confirmed_tickets}/{self.assigned_tickets})"

    class Meta:
        verbose_name = 'Familia'
        verbose_name_plural = 'Familias'


class Guest(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='guests', verbose_name='Familia')
    full_name = models.CharField('Nombre Completo', max_length=150)
    has_checked_in = models.BooleanField('¿Ingresó al evento?', default=False)
    check_in_time = models.DateTimeField('Hora de Ingreso', null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.family.name})"

    class Meta:
        verbose_name = 'Invitado'
        verbose_name_plural = 'Invitados'