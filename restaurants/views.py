import os
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Restaurant, Dish, Offer, Cart, Order, OrderItem, Address
from .recommendation import hybrid_recommendation
from .utils import generate_checksum, verify_checksum


# ===============================
# HOME PAGE
# ===============================
def home(request):

    query = request.GET.get('q')

    restaurants = Restaurant.objects.all()
    dishes = Dish.objects.all()

    if query:
        restaurants = Restaurant.objects.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(cuisine__icontains=query)
        )

        dishes = Dish.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(restaurant__name__icontains=query)
        )

    offers = Offer.objects.filter(
        valid_from__lte=date.today(),
        valid_to__gte=date.today()
    )

    return render(request, "home.html", {
        "restaurants": restaurants,
        "dishes": dishes,
        "offers": offers,
        "query": query
    })


# ===============================
# RESTAURANT DETAIL
# ===============================
def restaurant_detail(request, id):

    restaurant = get_object_or_404(Restaurant, id=id)
    dishes = Dish.objects.filter(restaurant=restaurant)

    return render(request, "restaurant_detail.html", {
        "restaurant": restaurant,
        "dishes": dishes
    })


# ===============================
# DISH DETAIL
# ===============================
def dish_detail(request, id):

    dish = get_object_or_404(Dish, id=id)

    offers = Offer.objects.filter(
        valid_from__lte=date.today(),
        valid_to__gte=date.today()
    )

    return render(request, "dish_detail.html", {
        "dish": dish,
        "offers": offers
    })


# ===============================
# RECOMMENDATION
# ===============================
@login_required(login_url='/accounts/login/')
def recommend_view(request):

    results = []

    if request.method == "POST":
        preferences = request.POST.get("preferences")
        results = hybrid_recommendation(preferences)

    return render(request, "dashboard.html", {
        "results": results
    })


# ===============================
# LOGOUT
# ===============================
def custom_logout(request):

    logout(request)
    return redirect("/")


# ===============================
# ADD TO CART
# ===============================
@login_required(login_url='/accounts/login/')
def add_to_cart(request, dish_id):

    dish = get_object_or_404(Dish, id=dish_id)

    cart_item = Cart.objects.filter(user=request.user, dish=dish).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, dish=dish, quantity=1)

    return redirect("cart")


# ===============================
# APPLY COUPON BUTTON
# ===============================
@login_required(login_url='/accounts/login/')
def apply_coupon(request, offer_id):

    try:

        offer = Offer.objects.get(
            id=offer_id,
            valid_from__lte=date.today(),
            valid_to__gte=date.today()
        )

        cart_items = Cart.objects.filter(user=request.user)

        item_total = sum(item.total_price() for item in cart_items)

        discount = int(item_total * offer.discount_percentage / 100)

        request.session["discount"] = discount
        request.session["offer_id"] = offer.id

    except Offer.DoesNotExist:

        request.session["discount"] = 0
        request.session["offer_id"] = None

    return redirect("cart")


# ===============================
# APPLY COUPON MANUAL
# ===============================
@login_required(login_url='/accounts/login/')
def apply_coupon_manual(request):

    if request.method == "POST":

        code = request.POST.get("coupon_code")

        try:

            offer = Offer.objects.get(
                code=code,
                valid_from__lte=date.today(),
                valid_to__gte=date.today()
            )

            cart_items = Cart.objects.filter(user=request.user)

            item_total = sum(item.total_price() for item in cart_items)

            discount = int(item_total * offer.discount_percentage / 100)

            request.session["discount"] = discount
            request.session["offer_id"] = offer.id

        except Offer.DoesNotExist:

            request.session["discount"] = 0
            request.session["offer_id"] = None

    return redirect("cart")


# ===============================
# CART VIEW
# ===============================
@login_required(login_url='/accounts/login/')
def cart_view(request):

    cart_items = Cart.objects.filter(user=request.user)

    item_total = sum(item.total_price() for item in cart_items)

    delivery_charge = 40
    gst = int(item_total * 0.05)

    coupon_discount = request.session.get("discount", 0)

    final_total = item_total + delivery_charge + gst - coupon_discount

    if final_total < 0:
        final_total = 0

    offers = Offer.objects.filter(
        valid_from__lte=date.today(),
        valid_to__gte=date.today()
    )

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "item_total": item_total,
        "delivery_charge": delivery_charge,
        "gst": gst,
        "discount": coupon_discount,
        "final_total": final_total,
        "offers": offers
    })


# ===============================
# REMOVE FROM CART
# ===============================
@login_required(login_url='/accounts/login/')
def remove_from_cart(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    item.delete()

    return redirect("cart")


# ===============================
# INCREASE QUANTITY
# ===============================
@login_required(login_url='/accounts/login/')
def increase_quantity(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    item.quantity += 1
    item.save()

    return redirect("cart")


# ===============================
# DECREASE QUANTITY
# ===============================
@login_required(login_url='/accounts/login/')
def decrease_quantity(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


# ===============================
# CHECKOUT
# ===============================
@login_required(login_url='/accounts/login/')
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    item_total = sum(item.total_price() for item in cart_items)

    delivery_charge = 40
    gst = int(item_total * 0.05)

    coupon_discount = request.session.get("discount", 0)

    total = item_total + delivery_charge + gst - coupon_discount

    addresses = Address.objects.filter(user=request.user)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "item_total": item_total,
        "delivery_charge": delivery_charge,
        "gst": gst,
        "discount": coupon_discount,
        "total": total,
        "addresses": addresses
    })


# ===============================
# PLACE ORDER
# ===============================
@login_required(login_url='/accounts/login/')
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart_items = Cart.objects.filter(user=request.user)

    item_total = sum(item.total_price() for item in cart_items)

    delivery_charge = 40
    gst = int(item_total * 0.05)

    coupon_discount = request.session.get("discount", 0)

    total = item_total + delivery_charge + gst - coupon_discount

    address = Address.objects.filter(user=request.user).last()

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_price=total
    )

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            dish=item.dish,
            quantity=item.quantity,
            price=item.dish.final_price()
        )

    cart_items.delete()

    request.session["discount"] = 0
    request.session["offer_id"] = None

    return render(request, "order_success.html")

# ===============================
# CONFIRM PAYMENT
# ===============================

@login_required(login_url='accounts/login/')
def confirm_payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    address = Address.objects.filter(user=request.user).last()

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_price=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            dish=item.dish,
            quantity=item.quantity,
            price=item.dish.final_price()
        )

    cart_items.delete()
    return redirect("orders")

# ===============================
# PAYTM PAYMENT
# ===============================
@login_required(login_url='accounts/login/')
def paytm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    amount = order.total_price
    paytm_params = {
        "MID": settings.PAYTM_MERCHANT_ID,
        "ORDER_ID": str(order.id),
        "CUST_ID": str(request.user.id),
        "TXN_AMOUNT": str(amount),
        "CHANNEL_ID": settings.PAYTM_CHANNEL_ID,
        "WEBSITE": settings.PAYTM_WEBSITE,
        "INDUSTRY_TYPE_ID": settings.PAYTM_INDUSTRY_TYPE_ID,
        "CALLBACK_URL": settings.PAYTM_CALLBACK_URL,
    }
    checksum = generate_checksum(paytm_params, settings.PAYTM_MERCHANT_KEY)
    paytm_params["CHECKSUMHASH"] = checksum
    paytm_url = "https://securegw-stage.paytm.in/order/process"
    return render(request, "paytm_redirect.html", {"paytm_url": paytm_url, "params": paytm_params})


@csrf_exempt
def paytm_callback(request):
    if request.method == "POST":
        received_data = dict(request.POST)
        verify = verify_checksum(received_data, settings.PAYTM_MERCHANT_KEY, received_data.get("CHECKSUMHASH", [None])[0])
        order_id = received_data.get("ORDERID", [None])[0]
        status = received_data.get("STATUS", [None])[0]

        if verify and status == "TXN_SUCCESS":
            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.save()
        return redirect("orders")


# ===============================
# ORDER HISTORY
# ===============================
@login_required(login_url='accounts/login/')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})


# ===============================
# SEARCH
# ===============================
def search(request):
    query = request.GET.get("q")
    dishes = Dish.objects.filter(
        Q(name__icontains=query) |
        Q(category__icontains=query) |
        Q(restaurant__name__icontains=query)
    )
    return render(request, "search.html", {"dishes": dishes})

# ===============================
# ORDER HISTORY
# ===============================
@login_required(login_url='/accounts/login/')
def order_history(request):

    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "orders.html", {
        "orders": orders
    })


# ===============================
# SEARCH
# ===============================
def search(request):

    query = request.GET.get("q")

    dishes = Dish.objects.filter(
        Q(name__icontains=query) |
        Q(category__icontains=query) |
        Q(restaurant__name__icontains=query)
    )

    return render(request, "search.html", {
        "dishes": dishes
    })