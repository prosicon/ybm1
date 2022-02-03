from django.urls import path
from django.conf.urls import url

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    #path('Hello/', views.hello, name='hello'),
    path('Productos/', views.ProductoListView.as_view(), name='Productos'),
    path('Producto/<int:pk>', views.ProductoDetailView.as_view(), name='Producto-detail'),
    path('Empresas/', views.EmpresaListView.as_view(), name='Empresas'),
    path('Empresa/<int:pk>',
         views.EmpresaDetailView.as_view(), name='Empresa-detail'),
]


urlpatterns += [
    path('myProductos/', views.LoanedProductosByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedProductosAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a Producto.
urlpatterns += [
    path('Producto/<uuid:pk>/renew/', views.renew_Producto_librarian, name='renew-Producto-librarian'),
]


# Add URLConf to create, update, and delete Empresas
urlpatterns += [
    path('Empresa/create/', views.EmpresaCreate.as_view(), name='Empresa-create'),
    path('Empresa/<int:pk>/update/', views.EmpresaUpdate.as_view(), name='Empresa-update'),
    path('Empresa/<int:pk>/delete/', views.EmpresaDelete.as_view(), name='Empresa-delete'),
]

# Add URLConf to create, update, and delete Productos
urlpatterns += [
    path('Producto/create/', views.ProductoCreate.as_view(), name='Producto-create'),
    path('Producto/<int:pk>/update/', views.ProductoUpdate.as_view(), name='Producto-update'),
    path('Producto/<int:pk>/delete/', views.ProductoDelete.as_view(), name='Producto-delete'),
]

urlpatterns += [
    path('Productos/busqueda/<str:produc>', views.busqueda, name='busqueda'),
    path('Empresa/busqueda/<str:empr>', views.busqueda_empresa, name='busqueda_empresa'),
    path('ajax/search/', views.search, name='ajax-search'),
    path('pdf/descargar/', views.descargar, name='pdf-descargar'),

]
