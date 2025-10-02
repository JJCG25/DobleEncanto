from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, DetallePedido, Producto, Cliente
from .forms import PedidoForm

# Crear pedido
def crear_pedido(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 1))

        # Para no usar clientes todavía, creamos un cliente genérico
        cliente, _ = Cliente.objects.get_or_create(nombre="Cliente Anónimo", defaults={
            'telefono': 'N/A',
            'direccion': 'N/A'
        })

        # Crear pedido
        pedido = Pedido.objects.create(cliente=cliente)

        # Crear detalle
        producto = Producto.objects.get(id=producto_id)
        DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)

        return redirect('crear_pedido')

    # Pedidos activos
    pedidos_activos = Pedido.objects.all().order_by('-fecha')

    return render(request, 'pedidos/crear_pedido.html', {
        'productos': productos,
        'pedidos_activos': pedidos_activos
    })

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
