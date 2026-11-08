from django import forms
from .models import Family

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'contact_phone', 'assigned_tickets']
        labels = {
            'name': 'Nombre de la Familia / Invitado principal',
            'contact_phone': 'Teléfono celular (10 dígitos o con lada)',
            'assigned_tickets': 'Boletos asignados',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-3 text-stone-900 focus:outline-none focus:ring-2 focus:ring-stone-800 text-sm uppercase',
                'placeholder': 'EJ. FAMILIA PÉREZ GONZÁLEZ / TÍO ROBERTO',
                'style': 'text-transform: uppercase;'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-3 text-stone-900 focus:outline-none focus:ring-2 focus:ring-stone-800 text-sm',
                'placeholder': 'Ej. 3312345678'
            }),
            'assigned_tickets': forms.NumberInput(attrs={
                'class': 'w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-3 text-stone-900 focus:outline-none focus:ring-2 focus:ring-stone-800 text-sm',
                'min': '1',
                'max': '30',
                'value': '2'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        return name.strip().upper()