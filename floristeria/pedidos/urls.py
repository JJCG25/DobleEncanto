from django.urls import path
from . import views

urlpatterns = [
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('productos/', views.catalogo_productos, name='catalogo_productos'),
    path('pedidos/estado/', views.lista_y_actualizar_pedidos, name='actualizar_estado'),
    path("clientes/registrar/", views.registrar_cliente, name="registrar_cliente"),
    path("historial/", views.historial_pedidos, name="historial_pedidos"),
    path("reportes/", views.reportes_ventas, name="reportes_ventas"),
    path('api/productos/', views.api_lista_productos, name='api_productos'),
    path('productos-externos/', views.productos_externos, name='productos_externos'),

]