from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('order-history/', views.history, name='history'),
    path('order-history/<str:order_date>/', views.order, name='order'),
    path('pdf/', views.orderfile, name='orderfile'),
    path('shed/', views.shed, name='shed'),
    path('shop/', views.shop, name='shop'),
    # path('temp/', views.temp, name='temp'),
]