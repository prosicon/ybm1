from django.test import TestCase

# Create your tests here.


from catalogo.models import Empresa
from django.urls import reverse


class EmpresaListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create Empresas for pagination tests
        number_of_Empresas = 13
        for Empresa_id in range(number_of_Empresas):
            Empresa.objects.create(descripcion='Christian {0}'.format(Empresa_id),
                                  nombre='Surname {0}'.format(Empresa_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalogo/Empresas/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('Empresas'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('Empresas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/Empresa_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('Empresas'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['Empresa_list']), 10)

    def test_lists_all_Empresas(self):
        # Get second page and confirm it has (exactly) the remaining 3 items
        response = self.client.get(reverse('Empresas')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['Empresa_list']), 3)


import datetime
from django.utils import timezone

from catalogo.models import ProductoInstance, Producto, Categoria, Beneficio
from django.contrib.auth.models import User  # Required to assign User as a borrower


class LoanedProductoInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a Producto
        test_Empresa = Empresa.objects.create(descripcion='John', nombre='Smith')
        test_categoria = Categoria.objects.create(name='Fantasy')
        test_beneficio = Beneficio.objects.create(name='English')
        test_Producto = Producto.objects.create(
            title='Producto Title',
            notas='My Producto notas',
            isbn='ABCDEFG',
            Empresa=test_Empresa,
            beneficio=test_beneficio,
        )
        # Create categoria as a post-step
        categoria_objects_for_Producto = Categoria.objects.all()
        test_Producto.categoria.set(categoria_objects_for_Producto)
        test_Producto.save()

        # Create 30 ProductoInstance objects
        number_of_Producto_copies = 30
        for Producto_copy in range(number_of_Producto_copies):
            return_date = timezone.now() + datetime.timedelta(days=Producto_copy % 5)
            if Producto_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            ProductoInstance.objects.create(Producto=test_Producto, imprint='Unlikely Imprint, 2016', due_back=return_date,
                                        borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalogo/myProductos/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalogo/Productoinstance_list_borrowed_user.html')

    def test_only_borrowed_Productos_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any Productos in list (none on loan)
        self.assertTrue('Productoinstance_list' in response.context)
        self.assertEqual(len(response.context['Productoinstance_list']), 0)

        # Now change all Productos to be on loan
        get_ten_Productos = ProductoInstance.objects.all()[:10]

        for copy in get_ten_Productos:
            copy.status = 'o'
            copy.save()

        # Check that now we have borrowed Productos in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('Productoinstance_list' in response.context)

        # Confirm all Productos belong to testuser1 and are on loan
        for Productoitem in response.context['Productoinstance_list']:
            self.assertEqual(response.context['user'], Productoitem.borrower)
            self.assertEqual(Productoitem.status, 'o')

    def test_pages_paginated_to_ten(self):

        # Change all Productos to be on loan.
        # This should make 15 test user ones.
        for copy in ProductoInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that only 10 items are displayed due to pagination
        # (if pagination not enabled, there would be 15 returned)
        self.assertEqual(len(response.context['Productoinstance_list']), 10)

    def test_pages_ordered_by_due_date(self):

        # Change all Productos to be on loan
        for copy in ProductoInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['Productoinstance_list']), 10)

        last_date = 0
        for copy in response.context['Productoinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


from django.contrib.auth.models import Permission  # Required to grant the permission needed to set a Producto as returned.


class RenewProductoInstancesViewTest(TestCase):

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()
        permission = Permission.objects.get(name='Set Producto as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a Producto
        test_Empresa = Empresa.objects.create(descripcion='John', nombre='Smith')
        test_categoria = Categoria.objects.create(name='Fantasy')
        test_beneficio = Beneficio.objects.create(name='English')
        test_Producto = Producto.objects.create(title='Producto Title', notas='My Producto notas',
                                        isbn='ABCDEFG', Empresa=test_Empresa, beneficio=test_beneficio,)
        # Create categoria as a post-step
        categoria_objects_for_Producto = Categoria.objects.all()
        test_Producto.categoria.set(categoria_objects_for_Producto)
        test_Producto.save()

        # Create a ProductoInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_Productoinstance1 = ProductoInstance.objects.create(Producto=test_Producto,
                                                              imprint='Unlikely Imprint, 2016', due_back=return_date,
                                                              borrower=test_user1, status='o')

        # Create a ProductoInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_Productoinstance2 = ProductoInstance.objects.create(Producto=test_Producto, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, borrower=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}))
        self.assertEqual(response.status_code, 403)


    def test_logged_in_with_permission_borrowed_Producto(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance2.pk}))

        # Check that it lets us login - this is our Producto and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_Producto(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users Producto
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalogo/Producto_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')

        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}),
                                    {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}),
                                    {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

    def test_redirects_to_all_borrowed_Producto_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-Producto-librarian', kwargs={'pk': self.test_Productoinstance1.pk}),
                                    {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_HTTP404_for_invalid_Producto_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our Productoinstance!
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-Producto-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)


class EmpresaCreateViewTest(TestCase):
    """Test case for the EmpresaCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set Producto as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a Producto
        test_Empresa = Empresa.objects.create(descripcion='John', nombre='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('Empresa-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalogo/Empresa/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('Empresa-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('Empresa-create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('Empresa-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/Empresa_form.html')

    def test_form_date_of_death_initially_set_to_expected_date(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('Empresa-create'))
        self.assertEqual(response.status_code, 200)

        expected_initial_date = datetime.date(2020, 6, 11)
        response_date = response.context['form'].initial['date_of_death']
        response_date = datetime.datetime.strptime(response_date, "%d/%m/%Y").date()
        self.assertEqual(response_date, expected_initial_date)

    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('Empresa-create'),
                                    {'descripcion': 'Christian Name', 'nombre': 'Surname'})
        # Manually check redirect because we don't know what Empresa was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalogo/Empresa/'))
