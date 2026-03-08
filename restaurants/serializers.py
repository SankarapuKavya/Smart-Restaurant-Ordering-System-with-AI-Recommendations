from rest_framework import serializers
from .models import Restaurant, Dish

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class DishSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = '__all__'

    def get_final_price(self, obj):
        return obj.final_price()