from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('order-history/', views.history, name='history'),
    path('order-history/<str:order_number>/', views.order, name='order'),
    path('archive/', views.archive, name='archive'),
    path('order-history/<str:order>', views.history, name='archive_year'),
    path('take-inventory/', views.take_inventory, name='take-inventory'),
    path('finalize/', views.finalize, name='finalize'),
    path('success/', views.success, name='success'),
    path('empty_order/', views.empty_order, name='empty_order'),
    path('analytics/', views.analytics, name='analytics'),
]