from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard')
]