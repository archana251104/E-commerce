from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from shop.models import Product

User = get_user_model()

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
    
    def get_total_items(self):
        return self.items.count()

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"