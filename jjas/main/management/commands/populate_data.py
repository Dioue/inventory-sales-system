from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from decimal import Decimal
from django.db import connection
from faker import Faker
import random
from collections import defaultdict
from datetime import timedelta, datetime
from ...models import (
    Category, Client, Unit, Product,
    BatchOrder, BatchOrderItem,
    SalesRecord, SalesRecordItem,
    Delivery, Supplier,
    DailySales, WeeklySales, MonthlySales
)

fake = Faker()

START_DATE = datetime(2024, 6, 1)
# Was 2027-06-29 (in the future relative to today) — capped at today so no
# sales/batch orders end up dated ahead of "now".
END_DATE = min(datetime(2027, 6, 29), datetime.today())

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
        Supplier.all_objects.all().delete()
        DailySales.all_objects.all().delete()
        WeeklySales.all_objects.all().delete()
        MonthlySales.all_objects.all().delete()

        self.stdout.write(self.style.WARNING('All existing records deleted.'))

        user = User.objects.first()

        # --- Groups & demo accounts: groups don't exist yet elsewhere, so created
        # fresh here (name only, no permissions attached). One demo account per
        # group with a fixed local/demo password. get_or_create so re-running the
        # command doesn't error on duplicate usernames (User isn't wiped above).
        self.stdout.write('Creating groups and demo accounts...')
        stocker_group, _ = Group.objects.get_or_create(name='Stocker')
        cashier_group, _ = Group.objects.get_or_create(name='Cashier')

        stocker_user, created = User.objects.get_or_create(
            username='stocker_demo',
            defaults={'email': 'stocker_demo@example.com'}
        )
        if created:
            stocker_user.set_password('password123')
            stocker_user.save()
        stocker_user.groups.add(stocker_group)

        cashier_user, created = User.objects.get_or_create(
            username='cashier_demo',
            defaults={'email': 'cashier_demo@example.com'}
        )
        if created:
            cashier_user.set_password('password123')
            cashier_user.save()
        cashier_user.groups.add(cashier_group)

        self.stdout.write('Creating categories...')
        category_names = [
            "Engine Components", "Suspension", "Braking System", "Transmission", "Electrical", 
            "Cooling System", "Exhaust", "Filters", "Steering", "Lighting"
        ]

        category_codes = ["MSX", "SUS", "BRK", "TRN", "ELC", "COL", "EXH", "FLT", "STR", "LIT"]
        categories = [
            Category(code=f"{category_codes[i]}{str(i).zfill(3)}", name=name, created_by=user)
            for i, name in enumerate(category_names)
        ]
        Category.objects.bulk_create(categories)
        reset_sequence(Category)

        self.stdout.write('Creating suppliers...')
        supplier_name = [
            "Alibaba", "CNFastwin", "HBHaolu", "AutoPartsHub", "GlobalParts",
        ]
        supplier = [
            Supplier(name=f"{str(i)}", address=fake.address(), contact_number=fake.phone_number()[:20], email=fake.email(), website=fake.url(), created_by=user)
            for i in supplier_name
        ]
        Supplier.objects.bulk_create(supplier)
        reset_sequence(Supplier)

        self.stdout.write('Creating clients...')
        clients = [
            Client(
                name=f"{fake.company()} Auto Parts",
                address_line_1=fake.street_address(),
                address_line_2=fake.secondary_address(),
                city=fake.city(),
                province=fake.state(),
                zip_code=fake.zipcode(),
                created_by=user
            ) for _ in range(300)
        ]
        Client.objects.bulk_create(clients)
        reset_sequence(Client)

        self.stdout.write('Creating units...')
        units = [Unit(name=unit, created_by=user) for unit in ['Piece', 'Box', 'Set', 'Roll', 'Liter', 'Gallon']]
        Unit.objects.bulk_create(units)
        reset_sequence(Unit)
        units = list(Unit.objects.all())

        categories = list(Category.objects.all())

        self.stdout.write('Creating products...')
        products = []

        part_names = [
            "Brake Pad", "Oil Filter", "Air Filter", "Alternator", "Timing Belt",
            "Fuel Injector", "Radiator", "Shock Absorber", "Spark Plug", "Clutch Disc",
            "Transmission Gear", "Steering Rack", "Drive Shaft", "Wheel Bearing", "CV Joint",
            "Engine Mount", "Fuel Pump", "Water Pump", "Ignition Coil", "Serpentine Belt",
            "Thermostat", "Control Arm", "Ball Joint", "Brake Caliper", "Camshaft",
            "Crankshaft", "Piston Ring", "Head Gasket", "Valve Cover", "Flywheel",
            "Throttle Body", "Oxygen Sensor", "Mass Air Flow Sensor", "Power Steering Pump", "Battery Cable",
            "Strut Assembly", "ABS Sensor", "Tie Rod End", "Exhaust Manifold", "Muffler",
            "Catalytic Converter", "Timing Chain", "Blower Motor", "AC Compressor", "Radiator Hose",
            "Fan Clutch", "Brake Rotor", "Windshield Wiper Motor", "Fuel Tank Cap", "Air Intake Hose"
        ]

        applications = [
            "Toyota", "Audi", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz",
            "Hyundai", "Nissan", "Kia", "Volkswagen", "Subaru", "Mazda", "Lexus",
            "Jeep", "Tesla", "Porsche", "Land Rover", "Volvo", "Mitsubishi"
        ]

        selected_parts = random.sample(part_names, 50)

        for i, part in enumerate(selected_parts):
            quantity = random.randint(5, 200)
            critical_level = random.randint(5, 50)

            if quantity < critical_level:
                status = 'Critical'
            elif quantity == critical_level:
                status = 'Low'
            else:
                status = 'Available'

            name = f"{part}"
            code = f"P{str(i+1).zfill(5)}"

            product = Product(
                name=name,
                code=code,
                category=random.choice(categories),
                unit=random.choice(units),
                application=random.choice(applications),
                side=random.choice(['Front', 'Rear']),
                description=f"A high-quality {part.lower()} suitable for various models.",
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
        batch_order_data = []
        suppliers = list(Supplier.objects.all())
        for i in range(843):
            date = random_date()
            bo = BatchOrder(
                supplier=random.choice(suppliers),
                purchase_date=date,
                grand_total=0,
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
            grand_total = 0
            items = []
            
            for _ in range(item_count):
                product = random.choice(products)
                quantity = random.randint(1, 20)
                cost_price = product.cost_price
                total_price = quantity * cost_price
                grand_total += total_price
                
                item = BatchOrderItem(
                    batch=bo,
                    product=product,
                    quantity=quantity,
                    cost_price=cost_price,
                    defective=random.randint(0, 3),
                    created_by=user,
                    date_added=bo.date_added,
                    date_modified=bo.date_modified
                )
                items.append(item)
                batch_items.append(item)

            batch_order_data.append((bo.id, grand_total))

        BatchOrderItem.objects.bulk_create(batch_items)
        reset_sequence(BatchOrderItem)

        for bo_id, total in batch_order_data:
            BatchOrder.objects.filter(id=bo_id).update(grand_total=round(total, 2))

        self.stdout.write('Creating sales records...')
        clients = list(Client.objects.all())
        sales_records = []
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

        sales_items = []
        for sr in sales_records:
            item_count = random.randint(1, 5)
            total = 0
            for _ in range(item_count):
                product = random.choice(products)
                quantity = random.randint(1, 10)
                base_total = product.selling_price * quantity
                surcharge = Decimal(str(round(float(base_total) * random.uniform(0.05, 0.25), 2)))
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

        # --- Deliveries: one per SalesRecord, chained off date_issued so dates
        # stay logically consistent (date_issued -> delivery_date -> date_claimed).
        # Sales issued too recently to plausibly be delivered yet are skipped —
        # still pending, realistically, rather than fabricating a future delivery.
        self.stdout.write('Creating deliveries...')
        today = datetime.today().date()
        deliveries = []
        for sr in sales_records:
            delivery_date = sr.date_issued + timedelta(days=random.choice([1, 2, 3, 5, 7]))
            if delivery_date > today:
                continue

            claim_lag = random.choice([0, 0, 1, 1, 2, 3])  # mostly on-time, some late
            date_claimed = min(delivery_date + timedelta(days=claim_lag), today)

            deliveries.append(Delivery(
                sale=sr,
                delivery_date=delivery_date,
                date_claimed=date_claimed,
                created_by=user,
                date_added=sr.date_issued,
                date_modified=sr.date_issued
            ))
        Delivery.objects.bulk_create(deliveries)
        reset_sequence(Delivery)

        # --- DailySales / WeeklySales / MonthlySales: populate_data bulk-creates
        # SalesRecords directly, bypassing SalesRecordSerializer.update_sales_aggregates()
        # (which normally maintains these incrementally on each real sale). These
        # blocks reproduce the same aggregation logic in bulk, so seeded data ends
        # up consistent with what the live API would have produced.
        self.stdout.write('Creating daily sales aggregates...')
        daily_totals = defaultdict(Decimal)
        for sr in sales_records:
            daily_totals[sr.date_issued] += sr.total

        daily_sales = [
            DailySales(date=date, total_sales=total, created_by=user)
            for date, total in daily_totals.items()
        ]
        DailySales.objects.bulk_create(daily_sales)
        reset_sequence(DailySales)

        self.stdout.write('Creating weekly sales aggregates...')
        weekly_totals = defaultdict(Decimal)
        for sr in sales_records:
            start_of_week = sr.date_issued - timedelta(days=sr.date_issued.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            weekly_totals[(start_of_week, end_of_week)] += sr.total

        weekly_sales = [
            WeeklySales(start_date=start, end_date=end, total_sales=total, created_by=user)
            for (start, end), total in weekly_totals.items()
        ]
        WeeklySales.objects.bulk_create(weekly_sales)
        reset_sequence(WeeklySales)

        self.stdout.write('Creating monthly sales aggregates...')
        monthly_totals = defaultdict(Decimal)
        for sr in sales_records:
            key = (sr.date_issued.year, sr.date_issued.month)
            monthly_totals[key] += sr.total

        monthly_sales = [
            MonthlySales(year=year, month=month, total_sales=total, created_by=user)
            for (year, month), total in monthly_totals.items()
        ]
        MonthlySales.objects.bulk_create(monthly_sales)
        reset_sequence(MonthlySales)

        self.stdout.write(self.style.SUCCESS('Successfully populated demonstration data.'))