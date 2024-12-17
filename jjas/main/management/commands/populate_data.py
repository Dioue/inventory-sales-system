from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from ...models import Category, Unit, Supplier, Product
import random
import string

class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Get the superuser (admin)
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Superuser (admin) does not exist.'))
            return

        # Function to generate the category code (For Categories)
        def generate_category_code():
            while True:
                # Generate 1-3 uppercase letters
                code = ''.join(random.choices(string.ascii_uppercase, k=random.randint(1, 3)))

                # Check if the generated code already exists
                if not Category.objects.filter(code=code).exists():
                    return code  # Return the unique code if it does not exist

        """ # Create Categories
        for _ in range(10):
            Category.objects.create(
                created_by=user,
                code=generate_category_code(),  # Using the new function to generate the code
                category_name=fake.unique.word()
            ) """

        """ # Create Units (UoM) with predefined valid values and ensure uniqueness
        valid_units = ['set', 'piece', 'box']

        for unit in valid_units:
            # Create the unit with a unique name
            Unit.objects.create(
                created_by=user,
                name=unit
            ) """

        """ # Create Suppliers
        for _ in range(5):
            # Generate a company name with common formats (Inc., Corp., Ltd, etc.)
            company_name = fake.company() + " " + random.choice(["Inc.", "Corp.", "Ltd", "Limited", "LLC", "Co.", "Group"])
            
            # Generate a phone number for the contact
            contact = fake.phone_number()

            Supplier.objects.create(
                created_by=user,
                name=company_name,
                contact=contact
            ) """


        # Function to generate a product code based on category code
        def generate_product_code(category_code):
            while True:
                # Generate 3-5 digits
                digits = ''.join(random.choices(string.digits, k=random.randint(3, 5)))
                # Combine the two parts with a dash in between
                product_code = f"{category_code}-{digits}"

                # Check if the generated code already exists in the Product model
                if not Product.objects.filter(name=product_code).exists():
                    return product_code  # Return the unique code if it does not exist


        # List of car brands and models for the application field
        car_brands_and_models = [
            "Toyota Corolla", "Honda Civic", "Ford Mustang", "Chevrolet Camaro", 
            "Tesla Model 3", "BMW 3 Series", "Audi A4", "Mercedes-Benz C-Class",
            "Hyundai Elantra", "Nissan Altima", "Volkswagen Jetta", "Kia Optima", 
            "Mazda 3", "Subaru Impreza", "Lexus IS", "Chrysler 300", 
            "Dodge Charger", "Porsche 911", "Jaguar F-Type", "Land Rover Range Rover"
        ]

        # Create Products
        for _ in range(20):
            # Pick a random category
            category = Category.objects.order_by('?').first()
            category_code = category.code  # Get the code of the chosen category

            product_status = fake.random_element(elements=('Available', 'Out of Stock', 'Critical'))
            
            Product.objects.create(
                created_by=user,
                name=generate_product_code(category_code),
                application=random.choice(car_brands_and_models),
                side=random.choice(["FRONT", "BACK", "REAR"]),
                description=fake.text(),
                image='',
                quantity_left=fake.random_int(min=0, max=100),
                cost_price=fake.random_number(digits=2),
                selling_price=fake.random_number(digits=3),
                critical_level=fake.random_int(min=1, max=10),
                product_status=product_status,
                unit=Unit.objects.order_by('?').first(),
                supplier=Supplier.objects.order_by('?').first(),
                category=category
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with random data'))
