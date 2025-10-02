from django.urls import path
from . import views

urlpatterns = [
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/lista_pedidos', views.lista_pedidos, name='lista_pedidos'),
    path('productos/', views.catalogo_productos, name='catalogo_productos'),
    path('pedidos/<int:pedido_id>/estado/', views.actualizar_estado, name='actualizar_estado'),
]