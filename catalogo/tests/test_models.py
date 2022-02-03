from django.test import TestCase

# Create your tests here.

from catalogo.models import Empresa


class EmpresaModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        Empresa.objects.create(descripcion='Big', nombre='Bob')

    def test_descripcion_label(self):
        Empresa = Empresa.objects.get(id=1)
        field_label = Empresa._meta.get_field('descripcion').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_nombre_label(self):
        Empresa = Empresa.objects.get(id=1)
        field_label = Empresa._meta.get_field('nombre').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_birth_label(self):
        Empresa = Empresa.objects.get(id=1)
        field_label = Empresa._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_death_label(self):
        Empresa = Empresa.objects.get(id=1)
        field_label = Empresa._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_descripcion_max_length(self):
        Empresa = Empresa.objects.get(id=1)
        max_length = Empresa._meta.get_field('descripcion').max_length
        self.assertEquals(max_length, 100)

    def test_nombre_max_length(self):
        Empresa = Empresa.objects.get(id=1)
        max_length = Empresa._meta.get_field('nombre').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_nombre_comma_descripcion(self):
        Empresa = Empresa.objects.get(id=1)
        expected_object_name = '{0}, {1}'.format(Empresa.nombre, Empresa.descripcion)

        self.assertEquals(str(Empresa), expected_object_name)

    def test_get_absolute_url(self):
        Empresa = Empresa.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(Empresa.get_absolute_url(), '/catalogo/Empresa/1')
