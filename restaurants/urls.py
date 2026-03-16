from django.urls import path
from . import views
from .api_views import restaurant_list_api

urlpatterns = [
    # Home & Search
    path('', views.home, name='home'),
    path("search/", views.home, name="home"),

    # Restaurant / Dish
    path('restaurant/<int:id>/', views.restaurant_detail, name='restaurant_detail'),
    path('dish/<int:id>/', views.dish_detail, name='dish_detail'),

    # AI Recommendation
    path('recommend/', views.recommend_view, name='recommend'),

    # REST API
    path('api/restaurants/', restaurant_list_api, name='restaurant_list_api'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('recommend/', views.recommend_view, name='recommend'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path("apply-coupon/<int:offer_id>/", views.apply_coupon, name="apply_coupon"),
    path("apply-coupon-manual/", views.apply_coupon_manual, name="apply_coupon_manual"),
    path('remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),

    # Checkout & Order
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),

    # Orders
    path('orders/', views.order_history, name='orders'),

    # Paytm Payment
    path("paytm/<int:order_id>/", views.paytm_payment, name="paytm_payment"),
    path("paytm/callback/", views.paytm_callback, name="paytm_callback"),
    path('logout/', views.custom_logout, name='custom_logout'),
]