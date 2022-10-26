from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('order-history/', views.history, name='history'),
    path('order-history/<str:order_date>/', views.order, name='order'),
    path('pdf/<str:order_date>', views.orderfile, name='orderfile'),
    path('shed/', views.take_inventory, name='shed'),
    path('shop/', views.take_inventory, name='shop'),
]