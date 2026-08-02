import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from shop.models import Category, Product
from django.core.files import File

# 1. CREATE CATEGORIES
print("📁 Creating categories...")
categories = ['Electronics', 'Clothing', 'Books', 'Home & Living', 'Sports']
for cat_name in categories:
    category, created = Category.objects.get_or_create(name=cat_name)
    print(f"{'✅ Created' if created else '📌 Found'} category: {cat_name}")

# Get category objects
electronics = Category.objects.get(name='Electronics')
clothing = Category.objects.get(name='Clothing')
books = Category.objects.get(name='Books')
home = Category.objects.get(name='Home & Living')

# 2. CREATE ALL PRODUCTS
print("\n🔄 Creating products...")

all_products = [
    # Electronics
    {'category': electronics, 'name': 'iPhone 15 Pro', 'price': 999.99, 
     'description': 'Latest smartphone with A17 chip and advanced features.', 'stock': 15},
    {'category': electronics, 'name': 'Samsung Galaxy S24', 'price': 899.99, 
     'description': 'Premium Android phone with AI features.', 'stock': 20},
    {'category': electronics, 'name': 'Sony WH-1000XM5', 'price': 299.99, 
     'description': 'Industry-leading noise cancelling headphones.', 'stock': 25},
    {'category': electronics, 'name': 'Apple Watch Series 9', 'price': 399.99, 
     'description': 'Smartwatch with health monitoring.', 'stock': 18},
    {'category': electronics, 'name': 'MacBook Air M2', 'price': 1099.99, 
     'description': 'Lightweight laptop with M2 chip.', 'stock': 10},
    {'category': electronics, 'name': 'iPad Pro 12.9"', 'price': 899.99, 
     'description': 'Powerful tablet with M2 chip.', 'stock': 12},
    {'category': electronics, 'name': 'AirPods Pro 2', 'price': 249.99, 
     'description': 'Wireless earbuds with noise cancellation.', 'stock': 30},
    {'category': electronics, 'name': 'LG OLED TV 65"', 'price': 1599.99, 
     'description': '65-inch 4K OLED Smart TV.', 'stock': 8},
    {'category': electronics, 'name': 'Canon EOS R5', 'price': 3899.99, 
     'description': 'Professional mirrorless camera.', 'stock': 5},
    {'category': electronics, 'name': 'Dell XPS 15', 'price': 1499.99, 
     'description': 'Premium Windows laptop.', 'stock': 12},
    
    # Clothing
    {'category': clothing, 'name': 'Nike Air Max 270', 'price': 149.99, 
     'description': 'Comfortable sneakers with Air cushioning.', 'stock': 40},
    {'category': clothing, 'name': "Levi's 501 Jeans", 'price': 79.99, 
     'description': 'Classic straight-fit denim jeans.', 'stock': 35},
    {'category': clothing, 'name': 'North Face Jacket', 'price': 249.99, 
     'description': 'Warm waterproof jacket.', 'stock': 20},
    {'category': clothing, 'name': 'Adidas Running Shorts', 'price': 34.99, 
     'description': 'Lightweight running shorts.', 'stock': 50},
    {'category': clothing, 'name': 'Polo Ralph Lauren Shirt', 'price': 89.99, 
     'description': 'Classic polo shirt.', 'stock': 30},
    {'category': clothing, 'name': 'Hoodie Sweatshirt', 'price': 59.99, 
     'description': 'Comfortable hoodie.', 'stock': 45},
    
    # Books
    {'category': books, 'name': 'Python Crash Course', 'price': 39.99, 
     'description': 'Introduction to Python programming.', 'stock': 25},
    {'category': books, 'name': 'Django for Beginners', 'price': 34.99, 
     'description': 'Build web apps with Django.', 'stock': 30},
    {'category': books, 'name': 'JavaScript: The Definitive Guide', 'price': 49.99, 
     'description': 'Comprehensive JavaScript guide.', 'stock': 20},
    {'category': books, 'name': 'Clean Code', 'price': 44.99, 
     'description': 'Handbook of software craftsmanship.', 'stock': 18},
    {'category': books, 'name': 'Design Patterns', 'price': 54.99, 
     'description': 'Reusable object-oriented software.', 'stock': 15},
    
    # Home & Living
    {'category': home, 'name': 'Smart LED Lamp', 'price': 49.99, 
     'description': 'Color changing smart lamp.', 'stock': 30},
    {'category': home, 'name': 'Robot Vacuum Cleaner', 'price': 299.99, 
     'description': 'Smart robot vacuum.', 'stock': 12},
    {'category': home, 'name': 'Coffee Maker', 'price': 89.99, 
     'description': 'Programmable coffee maker.', 'stock': 20},
    {'category': home, 'name': 'Bluetooth Speaker', 'price': 79.99, 
     'description': 'Portable waterproof speaker.', 'stock': 35},
    {'category': home, 'name': 'Air Purifier', 'price': 149.99, 
     'description': 'HEPA air purifier.', 'stock': 15},
]

added_count = 0
for p in all_products:
    product, created = Product.objects.get_or_create(
        name=p['name'],
        defaults=p
    )
    if created:
        added_count += 1
        print(f"✅ Added: {p['name']}")

print(f"\n✅ Added {added_count} new products!")
print(f"📊 Total products: {Product.objects.count()}")

# 3. ASSIGN IMAGES
print("\n🔄 Assigning images to products...")

product_images = {
    'iPhone 15 Pro': 'iphone.jpg',
    'Samsung Galaxy S24': 'iphone.jpg',
    'Sony WH-1000XM5': 'headphones.jpg',
    'Apple Watch Series 9': 'watch.jpg',
    'MacBook Air M2': 'laptop.jpg',
    'iPad Pro 12.9"': 'laptop.jpg',
    'AirPods Pro 2': 'headphones.jpg',
    'LG OLED TV 65"': 'laptop.jpg',
    'Canon EOS R5': 'laptop.jpg',
    'Dell XPS 15': 'laptop.jpg',
    'Nike Air Max 270': 'sneakers.jpg',
    "Levi's 501 Jeans": 'jeans.jpg',
    'North Face Jacket': 'jacket.jpg',
    'Adidas Running Shorts': 'tshirt.jpg',
    'Polo Ralph Lauren Shirt': 'tshirt.jpg',
    'Hoodie Sweatshirt': 'tshirt.jpg',
    'Python Crash Course': 'book.jpg',
    'Django for Beginners': 'book.jpg',
    'JavaScript: The Definitive Guide': 'book.jpg',
    'Clean Code': 'book.jpg',
    'Design Patterns': 'book.jpg',
    'Smart LED Lamp': 'lamp.jpg',
    'Robot Vacuum Cleaner': 'lamp.jpg',
    'Coffee Maker': 'coffee.jpg',
    'Bluetooth Speaker': 'speaker.jpg',
    'Air Purifier': 'lamp.jpg',
}

media_path = 'media/products/'
image_count = 0

for product_name, image_file in product_images.items():
    try:
        product = Product.objects.get(name=product_name)
        image_path = os.path.join(media_path, image_file)
        
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                product.image.save(image_file, File(f), save=True)
                print(f"✅ Added image to: {product_name}")
                image_count += 1
        else:
            print(f"❌ Image not found: {image_file} for {product_name}")
    except Product.DoesNotExist:
        print(f"❌ Product not found: {product_name}")

print(f"\n✅ Added images to {image_count} products!")
print("\n🎉 All done! Visit your store at http://127.0.0.1:8000/")