from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.urls import reverse
from django.db.models import F, Sum, Avg

import plotly.express as px

from datetime import datetime
from dateutil.relativedelta import relativedelta

from .models import Supplier, Item, Order
from .functions import createPDF, createCSV

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

        # Get most recent order number and add 1 for new order number
        try:
            order_number = Order.objects.values_list('order_number', flat=True).latest('order_number') + 1
        except:
            order_number = 1
        
        # Retrieve order data from session and save it to database
        # Update latest quantity for each item, taking the average of the last five order quantities
        for order in request.session['orders']:
            Order.objects.create(item_id=order[0], date=datetime.now(), order_qty=order[1], order_number=order_number)
            last_five_avg = Order.objects.filter(item_id=order[0]).order_by('-id')[:5].aggregate(avg=Avg('order_qty'))
            Item.objects.filter(id=order[0]).update(latest_qty = last_five_avg.get('avg'))

        # Get Administrator's Email Address
        user = User.objects.get(pk=1)

        # Retrieve supplier data from session and generate email for each supplier
        for supplier in request.session['suppliers']:
            # Get data associated with supplier from supplier table (Email, Phone)
            supplier_info = Supplier.objects.get(name=supplier)
            if supplier_info.send_email is True:
                recipient = supplier_info.email
            else:
                recipient = user.email
            # Get email message addressed to supplier from post request
            message = request.POST[supplier]
            # Generate PDF with supplier's items of non-zero order_qty
            pdf = createPDF(order_number=order_number, supplier=supplier)
            # Handle function usage errors
            if pdf is None:
                continue
            
            email = EmailMessage(
                subject='Order Form',
                body=message,
                from_email=user.email,
                to=[recipient],
            )
            email.attach(supplier + '_order.pdf', pdf.getvalue(), 'application/pdf')
            email.send(fail_silently=False)
        return HttpResponseRedirect(reverse('inventory:success'))
    return render(request, 'inventory/finalize.html', {'supplier_list': request.session['suppliers']})


@login_required
def history(request, order=None):
    if order:
        latest_orders = Order.objects.filter(date__year=order).distinct().order_by('-order_number')
        archive = 0
    else:
        latest_orders = Order.objects.all().values('date', 'order_number').distinct().order_by('-order_number')[:20]
        archive = Order.objects.all().values('date__year').distinct().order_by('-order_number')[20:]

    if request.method == "POST":
        return createCSV()

    return render(request, 'inventory/order-history.html', {'latest_orders': latest_orders, 'archive': archive})


@login_required
def archive(request):
    orders = Order.objects.all().values_list('date__year', flat=True).distinct()
    return render(request, 'inventory/archive.html', {'orders': orders})


@login_required
def order(request, order_number):
    orders = Order.objects.filter(order_number=order_number)

    if request.method == "POST":
        if request.POST.get('csv'):
            return createCSV(order_number)
        else:
            pdf = createPDF(orders=orders)
            return FileResponse(pdf, as_attachment=True, filename='order.pdf')

    return render(request, 'inventory/order.html', {'orders': orders})


@login_required
def analytics(request):
    # Fetch all items from the database
    items = Item.objects.all()
    product = '0'
    package = None

    # DEFAULT: Get total orders for each order date for year-to-date
    current_date = datetime.now()
    title = 'Orders: YTD'
    subtitle = ''
    start_date = current_date - relativedelta(years=1)

    # Frame the data according to user specification
    if request.method == "POST":
        frame = request.POST['frame']
        product = request.POST['product']
        if frame == 'month':
            title = 'Orders: Last Month'
            start_date = current_date - relativedelta(months=1)
        elif frame == 'all-time':
            title = 'Orders: All Time'
            start_date = current_date - relativedelta(years=500)
        
    
    # Retrieve orders from database according to requested range and item
    if product != '0':
        orders = Order.objects.filter(date__range=(start_date, current_date), item_id=product).values('date')\
            .annotate(sum=Sum('order_qty')).order_by('date')
        package = Item.objects.get(pk=product)
        if package.package:
            subtitle = ' - {} {}: {} of {} ea.'.format(package.brand, package.unit, package.package, package.package_qty)
        else:
            subtitle = ' - {} {}'.format(package.brand, package.unit)
            
    else:
        orders = Order.objects.filter(date__range=(start_date, current_date)).values('date')\
            .annotate(sum=Sum('order_qty')).order_by('date')
    
    # Organize values from queryset as ordered pairs divided into lists
    x_values = []
    y_values = []
    for order in orders:
        x_values.append(datetime.strftime(order['date'], "%m/%d/%Y"))
        y_values.append(order['sum'])

    # Generate line chart figure
    fig = px.line(
        data_frame = x_values,
        x = x_values,
        y = y_values,
        labels = {'x': 'Day', 'y': 'Total Order Quantity'},
        title = title + subtitle,
        color_discrete_sequence = ['black'],
        markers = True,
    )

    # Customize the look and feel of the chart
    fig.update_layout(
        xaxis = dict(
            showline = True,
            showgrid = True,
            linecolor = 'black',
        ),
        yaxis = dict(
            showline = True,
            showgrid = True,
            linecolor = 'black',
        ),
        plot_bgcolor = 'white',
        modebar_remove = ['select', 'lasso', 'pan', 'zoomin', 'zoomout', 'autoscale']
    )

    # Prepare figure to be passed to template
    chart = fig.to_html(config={'displaylogo': False})

    return render(request, 'inventory/analytics.html', {'chart': chart, 'items': items, 'package': package})


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
