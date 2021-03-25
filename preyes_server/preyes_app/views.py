from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from preyes_server.preyes_app.models import Customer, ProductItem, Category, TargetItem, TargetList
from preyes_server.preyes_app.serializers import CustomerSerializer, ProductItemSerializer, CategorySerializer, \
    TargetItemSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.core.mail import send_mail


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
def reset_password(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            customer = User.objects.get(username=data['username'])
            customer.set_password(data['password'])
            customer.save()
        except KeyError:
            return HttpResponse("Invalid request body", status=400)
        except User.DoesNotExist:
            return HttpResponse(f"The customer with the username {data['username']} does not exist", status=404)

        return HttpResponse("Successfully changed password!", status=200)


@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            customer = User.objects.get(username=data['email'])
            send_mail(
                'Reset Password',
                'This is a test message',
                'preyesapp@gmail.com',
                [customer.email]
            )
            return HttpResponse('Successfully sent the reset email', status=200)
        except KeyError:
            return HttpResponse(f"Request body is not valid", status=400)
        except User.DoesNotExist:
            return HttpResponse(f"No customer found with the email {data['email']}", status=404)
        except Exception as e:
            print(f'An error occurred {e}')


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
            categories = Category.objects.all().exclude(category_id='0')
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


@csrf_exempt
def register_device(request):
    from fcm_django.models import FCMDevice
    from preyes_server.settings import FCM_DJANGO_SETTING
    if request.method == 'POST':
        try:
            device = FCMDevice()
            data = JSONParser().parse(request)
            device.registration_id = data['registration_id']
            device.user = User.objects.get(id=data['id'])
            device.save()

            return JsonResponse("true", status=200, safe=False)
        except:
            return JsonResponse("false", status=400, safe=False)


@csrf_exempt
def crud_targetitem_targetlist(request, email):
    """
    Function allows crud actions on target items to targetlist

    POST: Input variables: target_price and product_item_reference_id
    """
    if check_session(request.session.session_key):
        try:
            # Get customer based on email
            customer = Customer.objects.get(email=email)

            # Get data from request body
            data = JSONParser().parse(request)

            # Check if customer has a target list otherwise create it
            target_list, created = TargetList.objects.get_or_create(customer_reference=customer)

            # Get the product item based on primary key
            product_item = ProductItem.objects.get(pk=data["product_item_reference_id"])

            # Make target item object to perform crud actions with
            target_item = TargetItem(product_item_reference=product_item,
                                     target_list_reference=target_list, target_price=data["target_price"])

        except Customer.DoesNotExist:
            return HttpResponse(status=404)

        # Add target item to target list
        if request.method == 'POST':

            # Check if specific target item already exists
            try:
                TargetItem.objects.get(product_item_reference=product_item,
                                       target_list_reference=target_list)
                return HttpResponse("Specific target item already exists")
            except TargetItem.DoesNotExist:

                # if target item does not exist yet,create it
                target_item_serializer = TargetItemSerializer(target_item, data=data, partial=True)
                if target_item_serializer.is_valid(raise_exception=True):
                    target_item_serializer.save()
                    return JsonResponse(target_item_serializer.data)
                return JsonResponse(target_item_serializer.errors, status=400)

        # update the target price of target item
        if request.method == 'PUT':
            target_item = TargetItem.objects.filter(product_item_reference=data["product_item_reference_id"],
                                                    target_list_reference=target_list).update(
                target_price=data["target_price"])
            return HttpResponse(target_item)

        # delete target item from a target list
        if request.method == 'DELETE':
            target_item = TargetItem.objects.filter(product_item_reference=data["product_item_reference_id"],
                                                    target_list_reference=target_list).delete()
            return HttpResponse(target_item)
    else:
        return HttpResponse(status=401)
