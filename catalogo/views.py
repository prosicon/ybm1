from django.shortcuts import render

# Create your views here.

from .models import Producto, Empresa, Categoria, ProductoInstance


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_Productos = Producto.objects.all().count()
    #num_instances = ProductoInstance.objects.all().count()
    # Available copies of Productos
    #num_instances_available = ProductoInstance.objects.filter(status__exact='a').count()
    num_Empresas = Empresa.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_Productos': num_Productos, 'num_Empresas': num_Empresas,
                 'num_visits': num_visits},
    )


from django.views import generic


class ProductoListView(generic.ListView):
    """Generic class-based view for a list of Productos."""
    model = Producto
    paginate_by = 10


class ProductoDetailView(generic.DetailView):
    """Generic class-based detail view for a Producto."""
    model = Producto


class EmpresaListView(generic.ListView):
    """Generic class-based list view for a list of Empresas."""
    model = Empresa
    paginate_by = 10


class EmpresaDetailView(generic.DetailView):
    """Generic class-based detail view for an Empresa."""
    model = Empresa


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedProductosByUserListView(LoginRequiredMixin, generic.ListView):
    #Generic class-based view listing Productos on loan to current user.
    model = ProductoInstance
    template_name = 'catalogo/Productoinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return ProductoInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedProductosAllListView(PermissionRequiredMixin, generic.ListView):
    #Generic class-based view listing all Productos on loan. Only visible to users with can_mark_returned permission.
    model = ProductoInstance
    permission_required = 'catalogo.can_mark_returned'
    template_name = 'catalogo/Productoinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return ProductoInstance.objects.filter(status__exact='o').order_by('due_back')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required

# from .forms import RenewProductoForm
from catalogo.forms import RenewProductoForm


@login_required
@permission_required('catalogo.can_mark_returned', raise_exception=True)
def renew_Producto_librarian(request, pk):
    #View function for renewing a specific ProductoInstance by librarian.
    Producto_instance = get_object_or_404(ProductoInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewProductoForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            Producto_instance.due_back = form.cleaned_data['renewal_date']
            Producto_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewProductoForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'Producto_instance': Producto_instance,
    }

    return render(request, 'catalogo/Producto_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Empresa


class EmpresaCreate(PermissionRequiredMixin, CreateView):
    model = Empresa
    fields = ['nombre', 'descripcion', 'direccion', 'telefono', 'email', 'facebook', 'web']
    #initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalogo.can_mark_returned'


class EmpresaUpdate(PermissionRequiredMixin, UpdateView):
    model = Empresa
    fields = ['nombre', 'descripcion', 'direccion', 'telefono', 'email', 'facebook', 'web'] #'__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'catalogo.can_mark_returned'


class EmpresaDelete(PermissionRequiredMixin, DeleteView):
    model = Empresa
    success_url = reverse_lazy('Empresas')
    permission_required = 'catalogo.can_mark_returned'


# Classes created for the forms challenge
class ProductoCreate(PermissionRequiredMixin, CreateView):
    model = Producto
    fields = ['nombre', 'Empresa', 'descripcion','categoria', 'beneficio']
    permission_required = 'catalogo.can_mark_returned'


class ProductoUpdate(PermissionRequiredMixin, UpdateView):
    model = Producto
    fields = ['nombre', 'Empresa', 'descripcion','categoria', 'beneficio']
    permission_required = 'catalogo.can_mark_returned'


class ProductoDelete(PermissionRequiredMixin, DeleteView):
    model = Producto
    success_url = reverse_lazy('Productos')
    permission_required = 'catalogo.can_mark_returned'

from django.http import HttpResponse
import json


def busqueda(request, produc):
        model = Producto
        p = Producto.objects.get(nombre=produc)
        #context = {'object': p}
        #return render(request, 'album/category_detail.html', context)
        #producto = Producto.objects.filter(nombre__exact= request.POST['nombre'] ).values('nombre')
        #return HttpResponse( p.id )
        #return reverse('Producto-detail', args=[str(p.id)])
        return HttpResponseRedirect(reverse('Producto-detail', args=[str(p.id)]))

def busqueda_empresa(request, empr):
        model = Empresa
        e = Empresa.objects.get(nombre=empr)
        #context = {'object': p}
        #return render(request, 'album/category_detail.html', context)
        #producto = Producto.objects.filter(nombre__exact= request.POST['nombre'] ).values('nombre')
        #return HttpResponse( p.id )
        #return reverse('Producto-detail', args=[str(p.id)])
        return HttpResponseRedirect(reverse('Empresa-detail', args=[str(e.id)]))



def hello(request):
    return HttpResponse("Hola...soy AJAX")

from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.contrib.auth.models import User
from django.core import serializers
import re
import json

def searching(request):

    # si no es una peticion ajax, devolvemos error 400
    if not request.is_ajax() or request.method != "POST":
        return HttpResponseBadRequest()

    # definimos el termino de busqueda
    q = request.POST['q']

    #verificamos si el termino de busqueda es un documento de identidad
    match = re.match(r'^(?P<CI>[0-9]{2,})$', q)
    isCI = (False, True)[match != None]

    # generamos la query
    if isCI:
        productos = Producto.objects.filter(CI=match.groupdict()['CI'])
    else:
        #users = Producto.objects.filter(nombre__contains=q)
        empresa = Empresa.objects.filter(nombre__contains = q)
        result = []

    for e in empresa:
        # Los campos que necesites
        result.append({
            "nombre": "",
            "empresa": e.nombre, # una relación a otro modelo
            "beneficio": "" # la misma relación, otro campo
        })

    # seleccionamos las columnas que deseamos obtener para el json
    producto_fields = (
        'nombre',
        'empresa',
        'beneficio'
    )
    data = json.dumps(result)
    # to json!
    #data = serializers.serialize('json', productos) #fields=producto_fields
    #data = serializers.serialize('json', "{nombre : Paris, empresa : Printex, beneficio : 100% desc} ", fields=producto_fields)
    # eso es todo por hoy ^^
    #return HttpResponse(data, content_type="application/json")
    return HttpResponse(data, content_type="application/json")


def search(request):

    # si no es una peticion ajax, devolvemos error 400
    if not request.is_ajax() or request.method != "POST":
        return HttpResponseBadRequest()

    # definimos el termino de busqueda
    q = request.POST['q']

    #verificamos si el termino de busqueda es un documento de identidad
    match = re.match(r'^(?P<CI>[0-9]{2,})$', q)
    isCI = (False, True)[match != None]

    # generamos la query
    if isCI:
        productos = Producto.objects.filter(CI=match.groupdict()['CI'])
    else:
        #users = Producto.objects.filter(nombre__contains=q)
        productos = Producto.objects.filter(nombre__contains = q)
        empresa = Empresa.objects.filter(nombre__contains = q)
        result = []
        for p in productos:
            # Los campos que necesites
            result.append({
                "nombre": p.nombre,
                "empresa": p.empresa.nombre, # una relación a otro modelo
                "beneficio": p.beneficio.nombre # la misma relación, otro campo
            })

        for e in empresa:
            # Los campos que necesites
            result.append({
                "nombre": "",
                "empresa": e.nombre, # una relación a otro modelo
                "beneficio": "" # la misma relación, otro campo
            })




    # seleccionamos las columnas que deseamos obtener para el json
    producto_fields = (
        'nombre',
        'empresa',
        'beneficio'
    )
    data = json.dumps(result)
    # to json!
    #data = serializers.serialize('json', productos) #fields=producto_fields
    #data = "[{'nombre' : 'Paris', 'empresa' : 'Printex', 'beneficio' : '100% desc'}] "
    # eso es todo por hoy ^^
    #return HttpResponse(data, content_type="application/json")
    return HttpResponse(data, content_type="application/json")

def descargar(request):
    file = "catalogo-yo-brillo-con-morelia.pdf"
    return render(
    request,
    'catalogo/descarga.html', context={
    'archivo': file})
