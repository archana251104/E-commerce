import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from shop.models import Product, Category
from django.core.files import File
from PIL import Image, ImageDraw

# ============================================
# STEP 1: CREATE PLACEHOLDER IMAGES IF MISSING
# ============================================
def create_placeholder_images():
    """Create placeholder images if they don't exist"""
    media_path = 'media/products/'
    os.makedirs(media_path, exist_ok=True)
    
    # Define placeholder images
    placeholders = [
        ('iphone.jpg', '📱 iPhone', '#007AFF'),
        ('headphones.jpg', '🎧 Headphones', '#1DB954'),
        ('watch.jpg', '⌚ Watch', '#34C759'),
        ('laptop.jpg', '💻 Laptop', '#A2A2A2'),
        ('tshirt.jpg', '👕 T-Shirt', '#FF6B6B'),
        ('jeans.jpg', '👖 Jeans', '#4A90D9'),
        ('book.jpg', '📘 Book', '#FF9500'),
        ('lamp.jpg', '💡 Lamp', '#FFD60A'),
        ('sneakers.jpg', '👟 Sneakers', '#FF2D55'),
        ('jacket.jpg', '🧥 Jacket', '#2C3E50'),
        ('coffee.jpg', '☕ Coffee', '#8B4513'),
        ('speaker.jpg', '🔊 Speaker', '#5856D6'),
    ]
    
    created_count = 0
    for filename, label, color in placeholders:
        filepath = os.path.join(media_path, filename)
        if not os.path.exists(filepath):
            try:
                img = Image.new('RGB', (800, 600), color=color)
                d = ImageDraw.Draw(img)
                d.text((400, 280), label, fill='white', anchor="mm")
                d.text((400, 330), 'Product Image', fill='#CCCCCC', anchor="mm")
                img.save(filepath)
                print(f"✅ Created placeholder: {filename}")
                created_count += 1
            except Exception as e:
                print(f"⚠️ Could not create {filename}: {e}")
    
    if created_count > 0:
        print(f"✅ Created {created_count} placeholder images")
    return created_count

# ============================================
# STEP 2: CHECK EXISTING IMAGES
# ============================================
media_path = 'media/products/'
print(f"\n🔍 Checking images in: {media_path}")

if not os.path.exists(media_path):
    print("📁 Creating media/products/ folder...")
    os.makedirs(media_path, exist_ok=True)

# Create placeholder images if needed
images = os.listdir(media_path) if os.path.exists(media_path) else []
valid_images = [f for f in images if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

if len(valid_images) < 5:
    print("⚠️ Not enough images found. Creating placeholders...")
    create_placeholder_images()
    images = os.listdir(media_path)
    valid_images = [f for f in images if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

print(f"📁 Found {len(valid_images)} images: {valid_images[:5]}...")

# ============================================
# STEP 3: CHECK PRODUCTS IN DATABASE
# ============================================
total_products = Product.objects.count()
print(f"\n📊 Found {total_products} products in database")

if total_products == 0:
    print("❌ No products found! Please add products first.")
    print("Run: python add_products.py")
    exit()

# ============================================
# STEP 4: ASSIGN IMAGES TO PRODUCTS
# ============================================
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

print("\n🔄 Assigning images to products...")
print("="*50)

added_count = 0
already_have_image = 0
not_found_products = []
missing_images = []

for product_name, image_file in product_images.items():
    try:
        product = Product.objects.get(name=product_name)
        
        # Skip if product already has an image
        if product.image and product.image.name:
            print(f"📌 Already has image: {product_name}")
            already_have_image += 1
            continue
            
        image_path = os.path.join(media_path, image_file)
        
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                product.image.save(image_file, File(f), save=True)
                print(f"✅ Added image to: {product_name}")
                added_count += 1
        else:
            print(f"❌ Image missing: {image_file} for {product_name}")
            missing_images.append(image_file)
            
    except Product.DoesNotExist:
        print(f"❌ Product not found: {product_name}")
        not_found_products.append(product_name)
    except Exception as e:
        print(f"⚠️ Error with {product_name}: {e}")

# ============================================
# STEP 5: SUMMARY
# ============================================
print("\n" + "="*50)
print("📊 SUMMARY")
print("="*50)
print(f"✅ Added new images: {added_count}")
print(f"📌 Already had images: {already_have_image}")
print(f"❌ Products not found: {len(not_found_products)}")
print(f"❌ Missing images: {len(missing_images)}")

if not_found_products:
    print(f"\n📋 Products not found:")
    for p in not_found_products[:10]:
        print(f"  • {p}")
    if len(not_found_products) > 10:
        print(f"  ... and {len(not_found_products) - 10} more")

if missing_images:
    print(f"\n📋 Missing image files:")
    for img in set(missing_images):
        print(f"  • {img}")

# ============================================
# STEP 6: SHOW ALL PRODUCTS WITH IMAGES
# ============================================
print("\n📊 All Products in Database:")
print("="*50)

# Group by category
categories = Category.objects.all()
for category in categories:
    products = Product.objects.filter(category=category)
    if products:
        print(f"\n📁 {category.name} ({products.count()} products):")
        for p in products:
            status = "🖼️" if p.image else "❌"
            print(f"  {status} {p.name} - ${p.price}")

# ============================================
# STEP 7: FINAL CHECK
# ============================================
products_without_images = Product.objects.filter(image='')
if products_without_images:
    print(f"\n⚠️ {products_without_images.count()} products still don't have images:")
    for p in products_without_images[:5]:
        print(f"  • {p.name}")
    if products_without_images.count() > 5:
        print(f"  ... and {products_without_images.count() - 5} more")
else:
    print("\n🎉 All products have images!")

print("\n✅ Done! Refresh your store to see the images.")