from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, Producto
from .forms import PedidoForm

# Crear pedido
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pedidos')
    else:
        form = PedidoForm()
    return render(request, 'pedidos/crear_pedido.html', {'form': form})

# Listar pedidos activos
def lista_pedidos(request):
    pedidos = Pedido.objects.filter(estado='pendiente')
    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})

# Catálogo de productos
def catalogo_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/catalogo.html', {'productos': productos})

# Actualizar estado de pedido
def actualizar_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
            return redirect('lista_pedidos')
    return render(request, 'pedidos/actualizar_estado.html', {'pedido': pedido, 'estados': Pedido.ESTADOS})

def inicio(request):
    return render(request, 'pedidos/inicio.html')
