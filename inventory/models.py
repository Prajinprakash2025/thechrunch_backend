from django.db import models

# 1. CREATE CATEGORY FIRST
class Category(models.Model):
    name = models.CharField(max_length=100) # e.g., "Smashed Burgers"
    image = models.ImageField(upload_to='category_images/', blank=True, null=True) # The circular icon
    
    def __str__(self):
        return self.name

# 2. THEN CREATE MENU ITEM
class MenuItem(models.Model):
    # Link to the Category
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE)
    
    # Core Details
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    
    # Pricing
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tags & Badges
    tag = models.CharField(max_length=50, blank=True, null=True) 
    is_best_seller = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name