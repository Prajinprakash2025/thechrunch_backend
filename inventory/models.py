from django.db import models

# 1. CATEGORY MODEL (Maps to "CATEGORY" dropdown)
class Category(models.Model):
    name = models.CharField(max_length=100) # e.g., "Burger"
    image = models.ImageField(upload_to='category_images/', blank=True, null=True) 
    
    def __str__(self):
        return self.name

# 2. SECTION MODEL (New: Maps to "SECTION" dropdown)
class Section(models.Model):
    name = models.CharField(max_length=100) # e.g., "Today's Special", "Combos"
    
    def __str__(self):
        return self.name

# 3. MENU ITEM / PRODUCT MODEL
class MenuItem(models.Model):
    # --- Dietary Choices ---
    DIETARY_CHOICES = [
        ('VEG', 'Veg'),
        ('NON-VEG', 'Non-Veg'),
    ]

    # --- Relationships (Dropdowns) ---
    section = models.ForeignKey(Section, related_name='menu_items', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE)
    
    # --- Core Details ---
    name = models.CharField(max_length=255, verbose_name="Product Name")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, verbose_name="Product Image")
    dietary_preference = models.CharField(max_length=10, choices=DIETARY_CHOICES, default='VEG')
    
    # --- Pricing & Inventory ---
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Actual ₹")
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Offer ₹")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Qty")
    
    # --- Metadata (Kept from your old model for good practice) ---
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name