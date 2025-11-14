from django import forms
from .models import Producto
from .models import Cliente

class PedidoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), label="Producto")
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad")

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion', 'correo']