from rest_framework import serializers
from .models import Category, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    # This will allow us to see the category details (like the name) instead of just an ID
    category_name = serializers.ReadOnlyField(source='category.name') 

    class Meta:
        model = MenuItem
        fields = '__all__'