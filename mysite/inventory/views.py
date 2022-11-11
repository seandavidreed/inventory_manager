from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.contrib.auth import get_user_model
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
    sent = False
    # Fetch only the names of suppliers that have items in the Item table
    supplier_list = Item.objects.values_list('supplier__name', flat=True).distinct()
    print(supplier_list)
    if request.method == "POST":
        # Get Administrator's Email Address
        email = get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True).first()
        for supplier in supplier_list:
            # Get data associated with supplier from supplier table (Email, Phone)
            supplier_info = Supplier.objects.get(name=supplier)
            # Get email message addressed to supplier from post request
            message = request.POST[supplier]
            # Generate PDF with supplier's items of non-zero order_qty
            pdf = createPDF(supplier=supplier)
            if pdf is None:
                continue
            email = EmailMessage(
                subject='Order Form',
                body=message,
                from_email=email,
                to=[supplier_info.email],
            )
            email.attach(supplier + '_order.pdf', pdf, 'application/pdf')
            email.send(fail_silently=False)
            sent = True
        return render(request, 'inventory/result.html', {'sent': sent})
    return render(request, 'inventory/finalize.html', {'supplier_list': supplier_list})


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
        pdf = createPDF(orders=orders, order_date=order_date)
        return FileResponse(pdf, as_attachment=True, filename='order.pdf')

    return render(request, 'inventory/order.html', {'orders': orders})


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')
