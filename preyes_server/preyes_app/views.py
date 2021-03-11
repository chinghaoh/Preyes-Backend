from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from preyes_server.preyes_app.models import Customer, ProductItem, Category
from preyes_server.preyes_app.serializers import CustomerSerializer, ProductItemSerializer, CategorySerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session


def check_session(session_id):
    valid_session = True
    try:
        Session.objects.get(pk=session_id)

    except Session.DoesNotExist:
        valid_session = False

    return valid_session


@csrf_exempt
def auth_login(request):
    """
    Login customer
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            login(request, user=user)
            try:
                customer = Customer.objects.get(email=data['username'])
                serializer = CustomerSerializer(customer)
            except Customer.DoesNotExist:
                return HttpResponse(status=404)

            return JsonResponse(serializer.data, status=200)
        else:
            return HttpResponse(status=400)


@csrf_exempt
def auth_logout(request):
    if request.method == 'POST':
        logout(request)


@csrf_exempt
def customer_list(request):
    """
    List all user customers, or create a new customer user.
    """
    if request.method == 'GET':
        if check_session(request.session.session_key):
            customers = Customer.objects.all()
            serializer = CustomerSerializer(customers, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return HttpResponse(status=401)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=data['email'],
                password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            serializer.save(auth_user_reference=user)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)



@csrf_exempt
def customer_detail(request, pk):
    """
    Retrieve, update or delete a customer
    """
    if check_session(request.session.session_key):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return JsonResponse(serializer.data)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = CustomerSerializer(customer, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        elif request.method == 'DELETE':
            customer.delete()
            return HttpResponse(status=204)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def product_item_list(request):
    """
    List all product_items.
    """
    if check_session(request.session.session_key):
        if request.method == 'GET':
            products = ProductItem.objects.all()
            serializer = ProductItemSerializer(products, many=True)
            return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def product_item_list_for_category(request):
    """
    List all product_items for a specific category.
    Use case 1: products returned based on category preferences of a customer
    Use case 2: products returned based on category filter
    """

    # Get a productlist based on user preferences or category filter
    if check_session(request.session.session_key):
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
            category_list = [category.category_id for category in customer.category_preference.all()]
        else:
            category_list = request.GET.get('categories').split(',')

        # Returns a product list based on the given categories
        try:
            category_objects = Category.objects.filter(category_id__in=category_list)
        except Category.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            products = ProductItem.objects.filter(category__in=category_objects)
            serializer = ProductItemSerializer(products, many=True)
            return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def product_item_detail(request, pk):
    """
    Retrieve, update or delete a product_item.
    """
    if check_session(request.session.session_key):
        try:
            product_item = ProductItem.objects.get(pk=pk)
        except ProductItem.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            serializer = ProductItemSerializer(product_item)
            return JsonResponse(serializer.data)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = ProductItemSerializer(product_item, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        elif request.method == 'DELETE':
            product_item.delete()
            return HttpResponse(status=204)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def all_categories(request):
    """
    List all categories
    """
    if check_session(request.session.session_key):
        if request.method == 'GET':
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def category_detail(request, pk):
    """
    Retrieve, update or delete a product_item.
    """
    if check_session(request.session.session_key):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            serializer = CategorySerializer(category)
            return JsonResponse(serializer.data)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = CategorySerializer(category, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        elif request.method == 'DELETE':
            category.delete()
            return HttpResponse(status=204)
    else:
        return HttpResponse(status=401)

