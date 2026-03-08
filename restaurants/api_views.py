from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Restaurant
from .serializers import RestaurantSerializer

@api_view(['GET'])
def restaurant_list_api(request):
    restaurants = Restaurant.objects.all()
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)