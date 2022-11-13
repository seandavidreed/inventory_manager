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
    
    # Get all items from database
    item_list = Item.objects.all()

    if request.method == "POST":
        # Declare list to store orders temporarily, until validated
        orders = []
        order_is_valid = False

        # Get values from template form one at a time
        for item in item_list:
            item_value = request.POST[str(item.id)]

            # If at least one item has a non-zero value, the order is valid
            if item_value != '0':
                order_is_valid = True

            # Append order data to orders list  
            orders.append(Order(item_id=item.id, date=datetime.datetime.now(), order_qty=item_value))
        
        # Validate the order and redirect if invalid
        if not order_is_valid:
            return render(request, 'inventory/result.html', {'sent': False})

        # Check if order already exists, else add order to the database
        if Order.objects.filter(date=datetime.datetime.now()).exists():
            return render(request, 'inventory/analytics.html')
        else:
            Order.objects.bulk_create(orders)

        # Go to final ordering stage to send emails
        return HttpResponseRedirect(reverse('inventory:finalize'))
    return render(request, 'inventory/take-inventory.html', {'item_list': item_list})


@login_required
def finalize(request):
    sent = False
    # Fetch only the names of suppliers that have items in the Item table
    supplier_list = Order.objects.values_list('item__supplier__name', flat=True).filter(date=datetime.datetime.now()).exclude(order_qty=0).distinct()
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
