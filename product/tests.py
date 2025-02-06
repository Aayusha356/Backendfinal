from django.test import TestCase
from .models import Category, Product, Customer, Order, OrderItem

class EcommerceTestCase(TestCase):
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(
            name="Electronics", 
            description="Devices and gadgets"
        )

        # Create a product
        self.product = Product.objects.create(
            name="Laptop",
            description="A high-end gaming laptop",
            price=1500.00,
            category=self.category
        )

        # Create a customer
        self.customer = Customer.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone="9876543210"
        )

        # Create an order
        self.order = Order.objects.create(
            customer=self.customer,
            total_price=1500.00
        )

        # Create an order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )

    def test_category_creation(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(self.category.name, "Electronics")
        self.assertEqual(self.category.description, "Devices and gadgets")

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.price, 1500.00)
        self.assertEqual(self.product.category, self.category)

    def test_customer_creation(self):
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(self.customer.first_name, "Jane")
        self.assertEqual(self.customer.last_name, "Doe")
        self.assertEqual(self.customer.email, "jane.doe@example.com")

    
    def test_order_creation(self):
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.total_price, 1500.00)

    def test_order_item_creation(self):
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 1)
