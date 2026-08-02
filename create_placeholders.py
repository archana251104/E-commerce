from PIL import Image, ImageDraw, ImageFont
import os

# Create folder if it doesn't exist
os.makedirs('media/products', exist_ok=True)

# Simple products with colors
products = [
    ('iphone.jpg', '📱 iPhone 15 Pro', '#007AFF'),
    ('headphones.jpg', '🎧 Sony Headphones', '#1DB954'),
    ('watch.jpg', '⌚ Apple Watch', '#34C759'),
    ('laptop.jpg', '💻 MacBook Air', '#A2A2A2'),
    ('tshirt.jpg', '👕 Cotton T-Shirt', '#FF6B6B'),
    ('jeans.jpg', '👖 Denim Jeans', '#4A90D9'),
    ('book.jpg', '📘 Python Book', '#FF9500'),
    ('lamp.jpg', '💡 Smart Lamp', '#FFD60A'),
    ('sneakers.jpg', '👟 Nike Air Max', '#FF2D55'),
    ('jacket.jpg', '🧥 Winter Jacket', '#2C3E50'),
    ('coffee.jpg', '☕ Coffee Maker', '#8B4513'),
    ('speaker.jpg', '🔊 Bluetooth Speaker', '#5856D6'),
]

for filename, label, color in products:
    # Create 800x600 image with color background
    img = Image.new('RGB', (800, 600), color=color)
    d = ImageDraw.Draw(img)
    
    # Add text (using white color instead of rgba)
    d.text((400, 280), label, fill='white', anchor="mm")
    d.text((400, 330), 'Product Image', fill='lightgray', anchor="mm")
    
    # Save
    img.save(f'media/products/{filename}')
    print(f"✅ Created: {filename}")

print("\n🎉 All placeholder images created!")
print(f"📁 Location: media/products/")