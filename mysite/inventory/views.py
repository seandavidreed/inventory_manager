from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.urls import reverse
from django.db.models import F, Sum

import plotly.express as px

import datetime
from dateutil.relativedelta import relativedelta

from .models import Supplier, Item, Order
from .functions import createPDF

# Create your views here.
@login_required
def take_inventory(request):
    
    # Get all items from database
    item_list_shed = Item.objects.filter(storage='A')
    item_list_shop = Item.objects.filter(storage='B')

    if request.method == "POST":
        # Prepare to store orders temporarily in session, until validated and transferred to database
        request.session['orders'] = []
        request.session['suppliers'] = {}
        order_is_valid = False

        # Get values from template form one at a time
        for item in item_list_shed:
            item_value = request.POST[str(item.id)]

            # If at least one item has a non-zero value, the order is valid
            if item_value != '0':
                order_is_valid = True
                request.session['suppliers'][item.supplier.name] = item.supplier.name

            # Append order data to session 
            request.session['orders'].append((item.id, item_value))

        # Get values from template form one at a time
        for item in item_list_shop:
            item_value = request.POST[str(item.id)]

            # If at least one item has a non-zero value, the order is valid
            if item_value != '0':
                order_is_valid = True
                request.session['suppliers'][item.supplier.name] = item.supplier.name

            # Append order data to session 
            request.session['orders'].append((item.id, item_value))
        
        # Validate the order and clear session and redirect if invalid
        if not order_is_valid:
            del request.session['suppliers']
            del request.session['orders']
            return HttpResponseRedirect(reverse('inventory:empty_order'))

        # Go to final ordering stage to send emails
        return HttpResponseRedirect(reverse('inventory:finalize'))
    return render(request, 'inventory/take-inventory.html', {'item_list_shed': item_list_shed, 'item_list_shop': item_list_shop})


@login_required
def finalize(request):
    if request.method == "POST":

        # Get most recent order number
        try:
            order_number = Order.objects.values_list('order_number', flat=True).latest('order_number') + 1
        except:
            order_number = 1
        

        # Retrieve order data from session and save it to database
        # Update latest quantity for each item, taking the average of the last two order quantities
        for order in request.session['orders']:
            Order.objects.create(item_id=order[0], date=datetime.datetime.now(), order_qty=order[1], order_number=order_number)
            Item.objects.filter(id=order[0]).update(latest_qty = (F('latest_qty') + order[1]) / 2)

        # Get Administrator's Email Address
        email = get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True).first()


        for supplier in request.session['suppliers']:
            # Get data associated with supplier from supplier table (Email, Phone)
            supplier_info = Supplier.objects.get(name=supplier)
            # Get email message addressed to supplier from post request
            message = request.POST[supplier]
            # Generate PDF with supplier's items of non-zero order_qty
            pdf = createPDF(order_number=order_number, supplier=supplier)
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
        return HttpResponseRedirect(reverse('inventory:success'))
    return render(request, 'inventory/finalize.html', {'supplier_list': request.session['suppliers']})


@login_required
def history(request, order=None):
    if order:
        latest_orders = Order.objects.filter(date__year=order).values('date', 'order_number').distinct().order_by('-order_number')
        archive = 0
    else:
        latest_orders = Order.objects.all().values('date', 'order_number').distinct().order_by('-order_number')[:20]
        archive = Order.objects.all().values('date__year').distinct().order_by('-order_number')[20:]
    return render(request, 'inventory/order-history.html', {'latest_orders': latest_orders, 'archive': archive})


@login_required
def archive(request):
    orders = Order.objects.all().values_list('date__year', flat=True).distinct()
    return render(request, 'inventory/archive.html', {'orders': orders})


@login_required
def order(request, order_number):
    orders = Order.objects.filter(order_number=order_number)

    if request.method == "POST":
        pdf = createPDF(orders=orders)
        return FileResponse(pdf, as_attachment=True, filename='order.pdf')

    return render(request, 'inventory/order.html', {'orders': orders})


@login_required
def analytics(request):
    # DEFAULT: Get total orders for each order date for year-to-date
    current_date = datetime.datetime.now()
    if request.method == "POST":
        title = 'Orders: Last Month'
        start_date = current_date - relativedelta(months=1)
    else:
        title = 'Orders: YTD'
        start_date = current_date - relativedelta(years=1)
    
    # Retrieve orders from database according to requested range 
    orders = Order.objects.filter(date__range=(start_date, current_date)).values('date__month', 'date__day', 'date__year').annotate(sum=Sum('order_qty'))
    x_values = []
    y_values = []

    # Organize values from queryset as ordered pairs divided into lists
    for order in orders:
        x_values.append(str(order['date__month']) + '/' + str(order['date__day']))
        y_values.append(order['sum'])

    # Generate line chart figure
    fig = px.bar(
        data_frame = x_values,
        x = x_values,
        y = y_values,
        range_y = [0, 200],
        labels = {'x': 'Day', 'y': 'Total Order Quantity'},
        title = title,
    )

    # Prepare figure to be passed to template
    chart = fig.to_html()

    return render(request, 'inventory/analytics.html', {'chart': chart})


@login_required
def success(request):
    return render(request, 'inventory/success.html')


@login_required
def empty_order(request):
    return render(request, 'inventory/empty-order.html')


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')
