from django.db import models
from django.contrib.auth.models import User


# =========================
# RESTAURANT
# =========================
class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=200)

    category = models.CharField(max_length=100, default="Restaurant")

    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)

    rating = models.FloatField(default=4.0)

    def __str__(self):
        return self.name


# =========================
# DISH
# =========================
class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    category = models.CharField(max_length=100)

    description = models.TextField()

    price = models.FloatField()

    image = models.ImageField(upload_to='dish_images/', null=True, blank=True)

    is_combo = models.BooleanField(default=False)

    discount_percentage = models.IntegerField(default=0)

    def final_price(self):
        if self.discount_percentage > 0:
            return self.price - (self.price * self.discount_percentage / 100)
        return self.price

    def __str__(self):
        return self.name


# =========================
# OFFERS
# =========================
class Offer(models.Model):
    code = models.CharField(max_length=50)

    title = models.CharField(max_length=200)

    description = models.TextField()

    discount_percentage = models.IntegerField()

    valid_from = models.DateField()

    valid_to = models.DateField()

    is_weekend_offer = models.BooleanField(default=False)

    is_festive_offer = models.BooleanField(default=False)

    def __str__(self):
        return self.code


# =========================
# ADDRESS
# =========================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    street = models.CharField(max_length=255)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.city}"


# =========================
# CART
# =========================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.dish.final_price() * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.dish.name} x {self.quantity}"


# =========================
# ORDER
# =========================
class Order(models.Model):

    STATUS_CHOICES = [
        ("Preparing", "Preparing"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Preparing"
    )

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


# =========================
# ORDER ITEMS
# =========================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.FloatField()

    def __str__(self):
        return f"{self.dish.name} - {self.quantity}"


# =========================
# RESTAURANT RATING
# =========================
class Rating(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating = models.IntegerField()

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}"