from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, DetallePedido, Producto, Cliente
from .forms import ClienteForm, PedidoForm
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from datetime import datetime
import calendar
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductoSerializer
from .models import Producto
import requests

@api_view(['GET'])
def api_lista_productos(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)


# Crear pedido
def crear_pedido(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    error = None  # Para mostrar mensajes de error

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 1))
        cliente_id = request.POST.get('cliente')

        # Validar que el cliente fue seleccionado
        if not cliente_id:
            error = "Debe seleccionar un cliente antes de crear el pedido."
        else:
            cliente = Cliente.objects.get(id=cliente_id)

            # Crear pedido
            pedido = Pedido.objects.create(cliente=cliente)

            # Crear detalle
            producto = Producto.objects.get(id=producto_id)
            DetallePedido.objects.create(
                pedido=pedido, producto=producto, cantidad=cantidad
            )

            return redirect('crear_pedido')

    # Pedidos activos
    pedidos_activos = Pedido.objects.all().order_by('-fecha')

    return render(request, 'pedidos/crear_pedido.html', {
        'productos': productos,
        'clientes': clientes,
        'pedidos_activos': pedidos_activos,
        'error': error
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
def lista_y_actualizar_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    pedido_seleccionado = None

    # Revisamos si se envió un POST de actualización de estado
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
        # Volvemos a cargar la página con el mismo pedido seleccionado
        pedido_seleccionado = pedido

    # Si se hizo GET con query param ?pedido=ID para seleccionar uno
    elif request.GET.get('pedido'):
        pedido_seleccionado = get_object_or_404(Pedido, id=request.GET.get('pedido'))

    return render(request, 'pedidos/actualizar_estado.html', {
        'pedidos': pedidos,
        'pedido_seleccionado': pedido_seleccionado,
        'estados': Pedido.ESTADOS
})

def registrar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrar_cliente')
    else:
        form = ClienteForm()

    clientes = Cliente.objects.all()

    return render(request, "pedidos/registrar_cliente.html", {
        "form": form,
        "clientes": clientes
    })

def historial_pedidos(request):
    clientes = Cliente.objects.all()
    pedidos = None
    cliente_seleccionado = None

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        
        if cliente_id:
            cliente_seleccionado = Cliente.objects.get(id=cliente_id)
            pedidos = Pedido.objects.filter(cliente=cliente_seleccionado)

    return render(request, "pedidos/historial.html", {
        "clientes": clientes,
        "pedidos": pedidos,
        "cliente_seleccionado": cliente_seleccionado
    })

def reportes_ventas(request):
    # ------- Mes seleccionado --------
    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]

    mes_seleccionado = int(request.POST.get("mes", 9))  # por defecto septiembre

    # ------- Filtrar pedidos del mes -------
    pedidos_mes = Pedido.objects.filter(fecha__month=mes_seleccionado)

    # ------- Totales -------
    total_pedidos = pedidos_mes.count()

    detalles_mes = DetallePedido.objects.filter(pedido__in=pedidos_mes)

    total_productos = detalles_mes.aggregate(
        total=Sum("cantidad")
    )["total"] or 0

    # ------- Total recaudado (CORRECTO) -------
    total_recaudado = detalles_mes.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("cantidad") * F("producto__precio"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    # ------- Productos más vendidos -------
    productos_vendidos = detalles_mes.values(
        "producto__nombre"
    ).annotate(total=Sum("cantidad")).order_by("-total")

    labels_productos = [p["producto__nombre"] for p in productos_vendidos]
    cantidades_productos = [p["total"] for p in productos_vendidos]

    # ------- Ventas mensuales (12 meses, en $$$) -------
    ventas_mensuales = []
    for mes in range(1, 13):
        pedidos_m = Pedido.objects.filter(fecha__month=mes)
        det_m = DetallePedido.objects.filter(pedido__in=pedidos_m)

        subtotal = det_m.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("cantidad") * F("producto__precio"),
                    output_field=DecimalField()
                )
            )
        )["total"] or 0

        ventas_mensuales.append(float(subtotal))

    return render(request, "pedidos/reportes.html", {
        "meses": meses,
        "mes_seleccionado": mes_seleccionado,

        "total_pedidos": total_pedidos,
        "total_productos": total_productos,
        "total_recaudado": total_recaudado,

        # TABLA
        "productos_vendidos": productos_vendidos,

        # JAVASCRIPT (listas ya listas!)
        "labels_productos": json.dumps(labels_productos),
        "cantidades_productos": json.dumps(cantidades_productos),
        "ventas_mensuales": json.dumps(ventas_mensuales)
    })


def productos_externos(request):
    API_URL = "https://monitor-dispatched-copy-shall.trycloudflare.com/api/export/productos"
    TOKEN = "811f4b3285cfb6b64645ddb1f4360cdecd0bfd1a3bff5fc57f6b08461bf9b7dd"

    headers = {"Authorization": f"Bearer {TOKEN}"}

    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()

        data = response.json()
        productos = data.get("data", [])

    except Exception as e:
        print("ERROR:", e)
        return render(request, "pedidos/productos_externos.html", {
            "productos_externos": [],
            "error": "No se pudieron obtener los productos externos."
        })

    return render(request, "pedidos/productos_externos.html", {
        "productos_externos": productos
    })



def inicio(request):
    return render(request, 'pedidos/inicio.html')
