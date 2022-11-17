from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('order-history/', views.history, name='history'),
    path('order-history/<str:order_number>/', views.order, name='order'),
    path('shed/', views.take_inventory, name='shed'),
    path('shop/', views.take_inventory, name='shop'),
    path('finalize/', views.finalize, name='finalize'),
    path('analytics/', views.analytics, name='analytics'),
]