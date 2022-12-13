from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', TemplateView.as_view(template_name='inventory/dashboard.html'), name='dashboard'),
    path('login/', TemplateView.as_view(template_name='inventory/login.html'), name='login'),
    path('empty_order/', TemplateView.as_view(template_name='inventory/empty-order.html'), name='empty_order'),
    path('delete-occurred/', TemplateView.as_view(template_name='inventory/delete-occurred.html'), name='delete-occurred'),
    path('no-data/', TemplateView.as_view(template_name='inventory/nodata.html'), name='nodata'),
    path('order-history/', views.history, name='history'),
    path('order-history/<str:order_number>/', views.order, name='order'),
    path('archive/', views.archive, name='archive'),
    path('order-history/<str:order>', views.history, name='archive_year'),
    path('take-inventory/', views.take_inventory, name='take-inventory'),
    path('finalize/', views.finalize, name='finalize'),
    path('success/', views.success, name='success'),
    path('analytics/', views.analytics, name='analytics'),
    path('delete-everything/', views.delete, name='delete'),
    path('csv/', views.all_data, name='all_data'),
]