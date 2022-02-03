from django.db import models
from django.core.validators import RegexValidator
#from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns


class Categoria(models.Model):
    """Model representing a Producto categoria (e.g. Science Fiction, Non Fiction)."""
    nombre = models.CharField(
        max_length=50,
        help_text="Ingresa la categoria(p. ej. Salud, Universidades)"
        )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.nombre


class Beneficio(models.Model):
    """Model representing a Beneficio (e.g. English, French, Japanese, etc.)"""
    nombre = models.CharField(max_length=200,
                            help_text="Ingresa el beneficio (p. ej. 10%)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.nombre


class Producto(models.Model):
    """Modelo que representa un servicio o producto"""
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey('Empresa', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because producto can only have one empresa, but las empresas can have multiple productos
    # Empresa as a string rather than object because it hasn't been declared yet in file.
    descripcion = models.TextField(max_length=1000, help_text="Aquí puedes detallar las características del descuento o beneficio")

    categoria = models.ManyToManyField('Categoria', help_text="Escoge un categoria de este servicio o producto")
    # ManyToManyField used because a categoria can contain many Productos and a Producto can cover many categorias.
    # Categoria class has already been defined so we can specify the object above.
    beneficio = models.ForeignKey('Beneficio', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['nombre', 'empresa']

    def display_categoria(self):
        """Creates a string for the Categoria. This is required to display categoria in Admin."""
        return ', '.join([categoria.nombre for categoria in self.categoria.all()[:3]])

    display_categoria.short_description = 'Categoría'

    def get_absolute_url(self):
        """Returns the url to access a particular Producto instance."""
        return reverse('Producto-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.nombre


import uuid  # Required for unique Producto instances
from datetime import date

from django.contrib.auth.models import User  # Required to assign User as a propietario


class ProductoInstance(models.Model):
    #Model representing a specific copy of a Producto (i.e. that can be borrowed from the library).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular Producto across whole library")
    Producto = models.ForeignKey('Producto', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    propietario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text=('Producto availability')
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set Producto as returned"),)

    def __str__(self):
        #String for representing the Model object.
        return '{0} ({1})'.format(self.id, self.Producto.nombre)



class Empresa(models.Model):
    """Model representing an Empresa."""
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telRegex = RegexValidator(regex = r"^\+?1?\d{10,15}$")
    telefono = models.CharField(validators = [telRegex], max_length = 16, unique = True,
                            help_text="Ingresa el teléfono a 10 dígitos")

    email = models.EmailField('email', null=True, blank=True)
    facebook = models.CharField(max_length=50, null=True, blank=True)
    webRegex = RegexValidator(regex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    web = models.CharField(validators = [webRegex], max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['nombre', 'descripcion']

    def get_absolute_url(self):
        """Returns the url to access a particular Empresa instance."""
        return reverse('Empresa-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.nombre, self.descripcion)
