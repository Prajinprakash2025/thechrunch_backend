from rest_framework import serializers
from .models import Category, Section, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# 1. ADDED SECTION SERIALIZER
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    # This will allow us to see the category details (like the name) instead of just an ID
    category_name = serializers.ReadOnlyField(source='category.name') 
    
    # 2. ADDED SECTION NAME 
    # This does the exact same thing for the new Section model
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = MenuItem
        fields = '__all__'