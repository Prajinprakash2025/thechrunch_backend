from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    # This will show these columns in the admin panel table
    list_display = ('headline', 'is_active', 'created_at')
    
    # This adds a filter sidebar to easily find active/inactive banners
    list_filter = ('is_active',)
    
    # This adds a search bar to search by headline
    search_fields = ('headline',)