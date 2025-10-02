from django.urls import path
from . import views

urlpatterns = [
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('productos/', views.catalogo_productos, name='catalogo_productos'),
    path('pedidos/estado/', views.lista_y_actualizar_pedidos, name='actualizar_estado'),

]