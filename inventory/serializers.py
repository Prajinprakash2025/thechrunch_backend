from rest_framework import serializers
from .models import Category, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    # This keeps the category name visible
    category_name = serializers.ReadOnlyField(source='category.name') 

    class Meta:
        model = MenuItem
        fields = '__all__'

    # ============================================================
    # 🛑 CUSTOM VALIDATION FOR SECTION LIMITS
    # ============================================================
    def validate(self, data):
        section = data.get('section')
        
        # You can define limits for any section here
        SECTION_LIMITS = {
            'BEST SELLER': 8,
            # 'TODAY'S SPECIAL': 5,  # You can add more limits like this if needed
        }

        if section in SECTION_LIMITS:
            limit = SECTION_LIMITS[section]
            
            # Check if we are creating a new item, or updating an existing item to a restricted section
            is_new_item = self.instance is None
            is_changing_section = not is_new_item and self.instance.section != section

            if is_new_item or is_changing_section:
                # Count how many items currently exist in this section
                current_count = MenuItem.objects.filter(section=section).count()
                
                if current_count >= limit:
                    raise serializers.ValidationError({
                        "section": f"Limit exceeded! You can only add up to {limit} products in the '{section}' section."
                    })
        
        return data