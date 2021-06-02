from django.http import HttpResponse, JsonResponse
import string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from rest_framework.parsers import JSONParser
from preyes_server.preyes_app.models import Customer, ProductItem, Category, TargetItem, TargetList, \
    PasswordChangeRequest
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
            password_request = PasswordChangeRequest.objects.get(GUID=data['GUID'])
            now = timezone.now()
            time_difference_minutes = (now - password_request.requested_at).total_seconds() / 60
            if time_difference_minutes <= 60.0:
                if not password_request.used:
                    customer = User.objects.get(username=password_request.email.email)
                    customer.set_password(data['password'])
                    customer.save()
                    password_request.used = True
                    password_request.save()
                else:
                    return HttpResponse(f"The link for the GUID {data['GUID']} has already been used", status=409)
            else:
                return HttpResponse(f"The link for the GUID {data['GUID']} has been expired", status=408)
        except KeyError:
            return HttpResponse("Invalid request body", status=400)
        except User.DoesNotExist:
            return HttpResponse(f"Could not find the customer for the given GUID", status=404)
        except PasswordChangeRequest.DoesNotExist:
            return HttpResponse(f"Could not find an entry with the GUID {data['GUID']}", status=404)

        return HttpResponse("Successfully changed password!", status=200)


@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            customer = User.objects.get(username=data['email'])
            customer_foreign = Customer.objects.get(auth_user_reference=customer)
            created_password_request = PasswordChangeRequest.objects.create(
                email=customer_foreign, GUID=get_random_string(12, allowed_chars=string.ascii_uppercase + string.digits)
            )
            body = f"Dear {customer_foreign.first_name} \n \n" \
                   f"Click the following link to reset your password: https://preyesapp.com/reset_password?GUID={created_password_request.GUID} \n \n" \
                   f"Kind regards, \n \n" \
                   f"Preyes Co"
            send_mail(
                'Reset Password',
                body,
                'preyesapp@gmail.com',
                [customer.email]
            )
            return HttpResponse('Successfully sent the reset email', status=200)
        except KeyError:
            return HttpResponse(f"Request body is not valid", status=400)
        except User.DoesNotExist:
            return HttpResponse(f"No customer found with the email {data['email']}", status=404)
        except Customer.DoesNotExist:
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

            # Check if customer has a target list otherwise create it
            target_list, created = TargetList.objects.get_or_create(customer_reference=customer)

            # Get data from request body
            if request.body:
                data = JSONParser().parse(request)

                # Get the product item based on primary key
                product_item = ProductItem.objects.get(pk=data["product_item_reference_id"])

        except Customer.DoesNotExist:
            return HttpResponse("Customer does not exist", status=404)

        except ProductItem.DoesNotExist:
            return HttpResponse("Product item does not exist", status=404)

        if request.method == 'GET':
            target_items = [item for item in TargetItem.objects.filter(target_list_reference=target_list)]
            serializer = TargetItemSerializer(target_items, many=True)
            return JsonResponse(serializer.data, safe=False)

        # Add target item to target list
        if request.method == 'POST':
            try:    
                # Make target item object to perform crud actions with
                target_item = TargetItem(
                    product_item_reference=product_item,
                    target_list_reference=target_list,
                    target_price=data['target_price'],
                    target_price_type=data['target_type']
                )
                # Check if specific target item already exists
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
                target_price=data['target_price'],
                target_price_type=data['target_type']
            )
            return HttpResponse(target_item)

        # delete target item from a target list
        if request.method == 'DELETE':
            target_item = TargetItem.objects.filter(product_item_reference=data["product_item_reference_id"],
                                                    target_list_reference=target_list).delete()
            return HttpResponse(target_item)
    else:
        return HttpResponse(status=401)


@csrf_exempt
def get_targetitem_targetlist(request, email, pk):
    """
    Function allows getting a specific target item from a targetlist

    POST: Input variables: target_price and product_item_reference_id
    """
    if check_session(request.session.session_key):
        try:
            # Get customer based on email
            customer = Customer.objects.get(email=email)

            # Check if customer has a target list otherwise create it
            target_list, created = TargetList.objects.get_or_create(customer_reference=customer)

            target_item = TargetItem.objects.get(product_item_reference=pk, target_list_reference=target_list)

        except Customer.DoesNotExist:
            return HttpResponse("No customer found with provided email", status=404)

        except TargetItem.DoesNotExist:
            return HttpResponse("No target item found", status=404)

        if request.method == 'GET':
            serializer = TargetItemSerializer(target_item)
            return JsonResponse(serializer.data)
    else:
        return HttpResponse(status=401)
