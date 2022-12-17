from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', TemplateView.as_view(template_name='inventory/dashboard.html'), name='dashboard'),
    path('login/', TemplateView.as_view(template_name='inventory/login.html'), name='login'),
    path('empty_order/', TemplateView.as_view(template_name='inventory/empty_order.html'), name='empty_order'),
    path('delete_occurred/', TemplateView.as_view(template_name='inventory/delete_occurred.html'), name='delete_occurred'),
    path('no_data/', TemplateView.as_view(template_name='inventory/no_data.html'), name='no_data'),
    path('email_error/', TemplateView.as_view(template_name='inventory/email_error.html'), name='email_error'),
    path('order_history/', views.history, name='history'),
    path('order_history/<str:order_number>/', views.order, name='order'),
    path('archive/', views.archive, name='archive'),
    path('order_history/<str:order>', views.history, name='archive_year'),
    path('take_inventory/', views.take_inventory, name='take_inventory'),
    path('finalize/', views.finalize, name='finalize'),
    path('success/', views.success, name='success'),
    path('analytics/', views.analytics, name='analytics'),
    path('delete_everything/', views.delete, name='delete'),
    path('csv/', views.all_data, name='all_data'),
]