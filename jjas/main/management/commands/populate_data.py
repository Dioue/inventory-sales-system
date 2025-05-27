from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from django.db import connection
from faker import Faker
import random
from datetime import timedelta, datetime
from ...models import (
    Category, Client, Unit, Product,
    BatchOrder, BatchOrderItem,
    SalesRecord, SalesRecordItem,
    Delivery
)

fake = Faker()

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 5, 27)

def random_date():
    return START_DATE + timedelta(
        days=random.randint(0, (END_DATE - START_DATE).days)
    )

def reset_sequence(model):
    with connection.cursor() as cursor:
        table = model._meta.db_table
        cursor.execute(
            f"SELECT setval(pg_get_serial_sequence('\"{table}\"', 'id'), (SELECT MAX(id) FROM \"{table}\"))"
        )

class Command(BaseCommand):
    help = 'Populate the database with demo data for system testing'

    def handle(self, *args, **kwargs):

        self.stdout.write('Clearing existing data...')

        # Delete from children to parents to avoid FK constraints
        Delivery.all_objects.all().delete()
        SalesRecordItem.all_objects.all().delete()
        SalesRecord.all_objects.all().delete()
        BatchOrderItem.all_objects.all().delete()
        BatchOrder.all_objects.all().delete()
        Product.all_objects.all().delete()
        Unit.all_objects.all().delete()
        Client.all_objects.all().delete()
        Category.all_objects.all().delete()

        self.stdout.write(self.style.WARNING('All existing records deleted.'))

        user = User.objects.first()

        self.stdout.write('Creating categories...')
        categories = [
            Category(
                code=f"CAT{str(i).zfill(4)}",
                name=fake.word(),
                created_by=user
            ) for i in range(1000)
        ]
        Category.objects.bulk_create(categories)
        reset_sequence(Category)

        self.stdout.write('Creating clients...')
        clients = [
            Client(
                name=fake.name(),
                address_line_1=fake.street_address(),
                address_line_2=fake.secondary_address(),
                city=fake.city(),
                province=fake.state(),
                zip_code=fake.zipcode(),
                created_by=user
            ) for _ in range(1000)
        ]
        Client.objects.bulk_create(clients)
        reset_sequence(Client)

        self.stdout.write('Creating units...')
        units = [Unit(name=unit, created_by=user) for unit in ['Piece', 'Box', 'Pack', 'Set']]
        Unit.objects.bulk_create(units)
        reset_sequence(Unit)
        units = list(Unit.objects.all())

        categories = list(Category.objects.all())
        
        

        self.stdout.write('Creating products...')
        products = []

        for i in range(1000):
            quantity = random.randint(10, 500)
            critical_level = random.randint(5, 500)

            if quantity < critical_level:
                status = 'Critical'
            elif quantity == critical_level:
                status = 'Low'
            else:
                status = 'Available'

            product = Product(
                name=f"{fake.word().capitalize()}{i}",
                code=f"P{str(i).zfill(5)}",
                category=random.choice(categories),
                unit=random.choice(units),
                application=fake.word(),
                side=fake.word(),
                description=fake.text(max_nb_chars=100),
                quantity=quantity,
                cost_price=round(random.uniform(100, 500), 2),
                selling_price=round(random.uniform(500, 1000), 2),
                critical_level=critical_level,
                status=status,
                created_by=user
            )

            products.append(product)
            
        Product.objects.bulk_create(products)
        reset_sequence(Product)
        products = list(Product.objects.all())

        self.stdout.write('Creating batch orders...')
        batch_orders = []
        batch_items = []
        for i in range(843):
            date = random_date()
            bo = BatchOrder(
                supplier=fake.company(),
                purchase_date=date,
                grand_total=random.randint(1000, 250000),
                created_by=user,
                date_added=date,
                date_modified=date
            )
            batch_orders.append(bo)
        BatchOrder.objects.bulk_create(batch_orders)
        reset_sequence(BatchOrder)
        batch_orders = list(BatchOrder.objects.all())

        for bo in batch_orders:
            item_count = random.randint(1, 5)
            for _ in range(item_count):
                product = random.choice(products)
                quantity = random.randint(1, 20)
                cost_price = product.cost_price
                item = BatchOrderItem(
                    batch=bo,
                    product=product,
                    quantity=quantity,
                    cost_price=cost_price,
                    defective=random.randint(0, 2),
                    created_by=user,
                    date_added=bo.date_added,
                    date_modified=bo.date_modified
                )
                batch_items.append(item)
        BatchOrderItem.objects.bulk_create(batch_items)
        reset_sequence(BatchOrderItem)

        self.stdout.write('Creating sales records...')
        clients = list(Client.objects.all())
        sales_records = []
        sales_items = []
        for i in range(1256):
            date_issued = random_date()
            net_day = 30
            due_date = date_issued + timedelta(days=net_day)
            sr = SalesRecord(
                client=random.choice(clients),
                date_issued=date_issued,
                due_date=due_date,
                net_day=net_day,
                total=0,
                created_by=user,
                date_added=date_issued,
                date_modified=date_issued
            )
            sales_records.append(sr)
        SalesRecord.objects.bulk_create(sales_records)
        reset_sequence(SalesRecord)
        sales_records = list(SalesRecord.objects.all())

        for sr in sales_records:
            item_count = random.randint(1, 5)
            total = 0
            for _ in range(item_count):
                product = random.choice(products)
                quantity = random.randint(1, 10)
                surcharge = Decimal(str(round(random.uniform(0, 100), 2)))
                item_total = product.selling_price * quantity + surcharge
                total += item_total
                item = SalesRecordItem(
                    sales_record=sr,
                    product=product,
                    quantity=quantity,
                    surcharge=surcharge,
                    total=item_total,
                    created_by=user,
                    date_added=sr.date_issued,
                    date_modified=sr.date_issued
                )
                sales_items.append(item)
            sr.total = total
        SalesRecord.objects.bulk_update(sales_records, ['total'])
        SalesRecordItem.objects.bulk_create(sales_items)
        reset_sequence(SalesRecordItem)

        self.stdout.write('Creating deliveries...')
        today = datetime.today().date()
        end_of_last_month = today.replace(day=1) - timedelta(days=1)
        start_of_last_month = end_of_last_month.replace(day=1)
        filtered_sales_records = [
            sr for sr in sales_records
            if start_of_last_month <= sr.date_issued <= end_of_last_month
        ]
        deliveries = [
            Delivery(
                sale=sr,
                delivery_date=sr.date_issued + timedelta(days=random.randint(1, 10)),
                date_claimed=min(sr.date_issued + timedelta(days=random.randint(5, 15)), today),  # Limit date_claimed to today's date
                created_by=user,
                date_added=sr.date_issued,
                date_modified=sr.date_issued
            ) for sr in filtered_sales_records
        ]
        Delivery.objects.bulk_create(deliveries)
        reset_sequence(Delivery)

        self.stdout.write(self.style.SUCCESS('Successfully populated demonstration data.'))
