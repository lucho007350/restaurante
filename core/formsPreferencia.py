from django import forms
from .models import PreferenciasUsuario  # Cambiado a PreferenciasUsuario (con 's')

class PreferenciasForm(forms.ModelForm):
    class Meta:
        model = PreferenciasUsuario  # Cambiado a PreferenciasUsuario
        fields = ['tipo_comida', 'tipo_bebida', 'tipo_proteina', 'rango_precio', 'incluir_promociones']  # Campos actualizados
        widgets = {
            'tipo_comida': forms.Select(attrs={'class': 'form-control'}),
            'tipo_bebida': forms.Select(attrs={'class': 'form-control'}),
            'tipo_proteina': forms.Select(attrs={'class': 'form-control'}),
            'rango_precio': forms.Select(attrs={'class': 'form-control'}),
            'incluir_promociones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'tipo_comida': '¿Qué tipo de comida prefieres?',
            'tipo_bebida': '¿Qué tipo de bebidas te gustan?',
            'tipo_proteina': '¿Qué tipo de proteína prefieres?',
            'rango_precio': '¿Cuál es tu rango de precio?',
            'incluir_promociones': '🔥 Mostrar solo productos en promoción',
        }