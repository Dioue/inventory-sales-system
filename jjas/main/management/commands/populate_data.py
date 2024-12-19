from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from ...models import Category, Unit, Supplier, Product, Client, SalesRecord, SalesRecordItem, Delivery
from datetime import timedelta, timezone as dt_timezone
from decimal import Decimal
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
            

        """ # Function to generate the category code (For Categories)
        def generate_category_code():
            while True:
                # Generate 1-3 uppercase letters
                code = ''.join(random.choices(string.ascii_uppercase, k=random.randint(1, 3)))

                # Check if the generated code already exists
                if not Category.objects.filter(code=code).exists():
                    return code  # Return the unique code if it does not exist

        # Create Categories
        for _ in range(25):
            Category.objects.create(
                created_by=user,
                code=generate_category_code(),  # Using the new function to generate the code
                name=fake.unique.word()
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


        # Function to generate a product code based on category code with 3 to 6 digits consisting of 0 and 9
        def generate_product_code():
            while True:
                # Generate one random letter at the beginning and end
                start_letter = random.choice(string.ascii_uppercase)
                end_letter = random.choice(string.ascii_uppercase)
                
                # Generate 3-6 digits using only '0' and '9'
                digits = ''.join(random.choices(['0', '9'], k=random.randint(2, 4)))

                # Combine letters and digits to create the product code
                product_code = f"{start_letter}{digits}{end_letter}"

                # Check if the generated code already exists in the Product model
                if not Product.objects.filter(code=product_code).exists():
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
        for _ in range(30):
            # Pick a random category
            category = Category.objects.order_by('?').first()
            category_code = category.code  # Get the code of the chosen category

            # Generate product attributes
            product_status = random.choice(['Available', 'Out of Stock', 'Critical'])

            Product.objects.create(
                created_by=user,  # Assuming `user` is defined elsewhere
                name=fake.unique.word().capitalize(),
                code=generate_product_code(),  # Match with `code` field
                application=random.choice(car_brands_and_models),
                side=random.choice(["FRONT", "BACK", "REAR"]),
                description=fake.text(max_nb_chars=100),
                image=None,  # Default to no image
                quantity_left=fake.random_int(min=0, max=100),
                cost_price=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                selling_price=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
                critical_level=fake.random_int(min=1, max=10),
                status=product_status,
                unit=Unit.objects.order_by('?').first(),
                supplier=Supplier.objects.order_by('?').first(),
                category=category
            )

        print('Successfully populated the database with random data.')

        
        """ self.stdout.write(self.style.SUCCESS('Creating Clients...'))
        for _ in range(20):
            Client.objects.create(
                created_by=user,
                name=fake.company(),
                address=fake.address()
            )

        self.stdout.write(self.style.SUCCESS('Clients created successfully.'))

        # Create Sales Records and Sales Items
        self.stdout.write(self.style.SUCCESS('Creating Sales Records and Sales Items...'))
        clients = list(Client.objects.all())
        products = list(Product.objects.all())

        if not products:
            self.stdout.write(self.style.ERROR('No products available to create sales items. Please populate products first.'))
            return

        for _ in range(40):
            # Pick a random client
            client = random.choice(clients)

            # Generate a sales record
            net_day = random.choice([0, 15, 30, 60, 90])
            date_issued = fake.date_this_year()

            # Create Sales Record
            sales_record = SalesRecord.objects.create(
                created_by=user,
                client=client,
                date_issued=date_issued,
                net_day=net_day,
                total=0,  # Initial total (will be updated after creating items)
                order_status=random.choice(['Unpaid', 'Paid'])
            )

            sales_items = []
            total_amount = Decimal('0.00')

            for _ in range(random.randint(1, 25)):
                product = random.choice(products)
                quantity = random.randint(1, 10)
                surcharge = Decimal(round(random.uniform(0, 50), 2))  # Convert to Decimal
                amount = (product.selling_price * quantity) + surcharge

                # Create sales record item
                sales_item = SalesRecordItem(
                    sales_record=sales_record,
                    product=product,
                    quantity=quantity,
                    surcharge=surcharge,
                    amount=amount
                )
                sales_items.append(sales_item)
                total_amount += amount

            # Bulk create sales items for efficiency
            SalesRecordItem.objects.bulk_create(sales_items)

            # Update the sales record total with the accumulated amount
            sales_record.total = round(total_amount, 2)
            sales_record.save()

        self.stdout.write(self.style.SUCCESS('Sales Records and Sales Items created successfully.'))


        # Create Deliveries
        self.stdout.write(self.style.SUCCESS('Creating Deliveries...'))
        sales_records = list(SalesRecord.objects.all())  # Get all sales records
        for _ in range(350):
            # Pick a random sales record
            sales_record = random.choice(sales_records)

            # Generate a delivery
            delivery_date = fake.date_time_this_year(tzinfo=dt_timezone.utc)
            claimed_date = delivery_date + timedelta(days=random.randint(1, 30))  # Claim date within 30 days after delivery

            Delivery.objects.create(
                created_by=user,
                client=sales_record.client,  # Assuming Delivery is associated with SalesRecord's client
                delivery_date=delivery_date,
                date_claimed=claimed_date,
            )

        self.stdout.write(self.style.SUCCESS('Deliveries created successfully.')) """