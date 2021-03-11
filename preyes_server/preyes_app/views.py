from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from preyes_server.preyes_app.models import Customer, ProductItem, Category
from preyes_server.preyes_app.serializers import CustomerSerializer, ProductItemSerializer, CategorySerializer
from django.contrib.auth.models import User


@csrf_exempt
def customer_list(request):
    """
    List all user customers, or create a new customer user.
    """
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return JsonResponse(serializer.data, safe=False)

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


@csrf_exempt
def product_item_list(request):
    """
    List all product_items.
    """
    if request.method == 'GET':
        products = ProductItem.objects.all()
        serializer = ProductItemSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def product_item_list_for_category(request):
    """
    List all product_items for a specific category.
    Use case 1: products returned based on category preferences of a customer
    Use case 2: products returned based on category filter
    """

    # Get a productlist based on user preferences or category filter
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


@csrf_exempt
def product_item_detail(request, pk):
    """
    Retrieve, update or delete a product_item.
    """
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


@csrf_exempt
def all_categories(request):
    """
    List all categories
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def category_detail(request, pk):
    """
    Retrieve, update or delete a product_item.
    """
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


