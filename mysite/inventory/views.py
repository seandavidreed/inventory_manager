from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.core.mail import EmailMessage
from django.urls import reverse
import datetime

from .models import Supplier, Item, Order
from .functions import createPDF

# Create your views here.
@login_required
def take_inventory(request):
    if request.path == '/inventory/shed/':
        item_list = Item.objects.filter(storage__contains='A')
        next_page = 'inventory:finalize'
    else:
        item_list = Item.objects.filter(storage__contains='B')
        next_page = 'inventory:shed'

    if request.method == "POST":
        for item in item_list:
            item_value = request.POST[str(item.id)]
            order, was_created = Order.objects.get_or_create(date=datetime.datetime.now(), item_id=item.id)
            order.order_qty = item_value
            order.save()
        return HttpResponseRedirect(reverse(next_page))
    return render(request, 'inventory/take-inventory.html', {'item_list': item_list})


@login_required
def finalize(request):
    supplier_list = Supplier.objects.get(pk=2)
    if request.method == "POST":
        message = request.POST['message']
        pdf = createPDF()
        email = EmailMessage(
            subject='Order Form',
            body=message,
            from_email='seanreed7992@gmail.com',
            to=[supplier_list.email],
        )
        email.attach('orderform.pdf', pdf, 'application/pdf')
        email.send(fail_silently=False)
        return HttpResponseRedirect(reverse('inventory:success'))
    return render(request, 'inventory/finalize.html', {'supplier_list': supplier_list})


@login_required
def success(request):
    return render(request, 'inventory/success.html')


@login_required
def analytics(request):
    return render(request, 'inventory/analytics.html')


@login_required
def history(request):
    order_list = Order.objects.all().values('date').distinct().order_by('-date')
    return render(request, 'inventory/order-history.html', {'order_list': order_list})


@login_required
def order(request, order_date):
    orders = Order.objects.filter(date=order_date)

    if request.method == "POST":
        pdf = createPDF(orders, order_date)
        return FileResponse(pdf, as_attachment=True, filename='order.pdf')

    return render(request, 'inventory/order.html', {'orders': orders})


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')
