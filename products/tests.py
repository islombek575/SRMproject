from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

class ProductTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', email='admin@test.com', password='admin123')
        self.client.login(username='admin', password='admin123')
        self.product = Product.objects.create(name='Test Product', price=10, quantity=5)

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_product_create(self):
        response = self.client.post(reverse('product_create'), {
            'name': 'New Product',
            'price': 20,
            'quantity': 2
        })
        self.assertEqual(Product.objects.count(), 2)

    def test_product_update(self):
        response = self.client.post(reverse('product_update', args=[self.product.id]), {
            'name': 'Updated Product',
            'price': 15,
            'quantity': 3
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')

    def test_product_delete(self):
        response = self.client.post(reverse('product_delete', args=[self.product.id]))
        self.assertEqual(Product.objects.count(), 0)
