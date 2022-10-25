from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('shed/', views.shed, name='shed'),
    path('shop/', views.shop, name='shop'),
    # path('temp/', views.temp, name='temp'),
]