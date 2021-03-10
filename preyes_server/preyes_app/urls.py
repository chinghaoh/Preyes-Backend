from preyes_server.preyes_app import views
from django.urls import path

urlpatterns = [
    path('customers/', views.customer_list),
    path('customers/<int:pk>/', views.customer_detail),
]
