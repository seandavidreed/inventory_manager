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
from .functions import create_pdf, create_csv, read_csv

# Create your views here.
@login_required
def take_inventory(request):
    
    # Get all items from database
    item_list_shed = Item.objects.filter(storage='A')
    item_list_shop = Item.objects.filter(storage='B')

    if request.method == "POST":
        # Prepare to store orders and info in session
        request.session['orders'] = []
        request.session['suppliers'] = {}
        order_is_valid = False

        # Get values from template form
        for item in [*item_list_shed, *item_list_shop]:
            item_value = request.POST[str(item.id)]

            # If at least one item has a non-zero value, the order is valid
            if item_value != '0':
                order_is_valid = True
                request.session['suppliers'][item.supplier.name] = (item.supplier.name, item.supplier.email, item.supplier.send_email)

            # Append order data to session 
            request.session['orders'].append((item.id, item_value))
        
        if not order_is_valid:
            del request.session['suppliers']
            del request.session['orders']
            return HttpResponseRedirect(reverse('inventory:empty_order'))

        return HttpResponseRedirect(reverse('inventory:finalize'))

    return render(request, 'inventory/take_inventory.html', {'item_list_shed': item_list_shed, 'item_list_shop': item_list_shop})


@login_required
def finalize(request):

    # Supplier send_email field is True, add them to the list
    session_data = request.session['suppliers']
    supplier_list = []
    for key in session_data:
        if session_data[key][2] is True:
            supplier_list.append(session_data[key][0:2])

    if request.method == "POST":

        request.session['csv'] = {}

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

        # Retrieve supplier data from session and generate email for each supplier where send_email = True
        for supplier in session_data:
            # Get data associated with supplier from supplier table (Email, Phone)
            supplier_info = Supplier.objects.get(name=supplier)
            if supplier_info.send_email is False:
                request.session['csv'][supplier] = (order_number, supplier)
                continue

            message = request.POST[supplier]

            pdf = create_pdf(order_number=order_number, supplier=supplier)
            if pdf is None:
                continue
            
            email = EmailMessage(
                subject='Order Form',
                body=message,
                from_email=user.email,
                to=[supplier_info.email],
            )
            email.attach(supplier + '_order.pdf', pdf.getvalue(), 'application/pdf')
            try:
                email.send(fail_silently=False)
            except:
                return HttpResponseRedirect(reverse('inventory:email_error'))

        return HttpResponseRedirect(reverse('inventory:success'))

    return render(request, 'inventory/finalize.html', {'supplier_list': supplier_list})


def success(request):

    # Get suppliers where send_email = False
    # Allow user to download their order info as csv
    suppliers = []
    csv = request.session['csv']
    for key in csv:
        suppliers.append(csv[key][1])

    if request.method == "POST":
        choice = request.POST['supplier']
        file = create_csv(order_number=csv[choice][0], supplier=choice)
        return file
    return render(request, 'inventory/success.html', {'suppliers': suppliers})



@login_required
def history(request, order=None):

    # If number of orders exceeds 20, collapse the rest into an archive
    if order:
        latest_orders = Order.objects.values('date', 'order_number').filter(date__year=order).distinct().order_by('-order_number')
        archive = 0
    else:
        latest_orders = Order.objects.values('date', 'order_number').distinct().order_by('-order_number')[:20]
        archive = Order.objects.all().values('date__year').distinct().order_by('-order_number')[20:]

    if request.method == "POST":
        return create_csv()

    return render(request, 'inventory/order_history.html', {'latest_orders': latest_orders, 'archive': archive})


@login_required
def archive(request):
    orders = Order.objects.all().values_list('date__year', flat=True).distinct().order_by('-date__year')
    return render(request, 'inventory/archive.html', {'orders': orders})


@login_required
def order(request, order_number):
    orders = Order.objects.filter(order_number=order_number)

    if request.method == "POST":
        if request.POST.get('csv'):
            return create_csv(order_number)
        else:
            pdf = create_pdf(orders=orders)
            return FileResponse(pdf, as_attachment=True, filename=str(orders[0].date) + '_order_' + order_number  + '.pdf')

    return render(request, 'inventory/order.html', {'orders': orders})


@login_required
def analytics(request):

    items = Item.objects.all().order_by('unit')
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
        orders = Order.objects.filter(date__range=(start_date, current_date), item_id=product).exclude(order_qty=0).values('date')\
            .annotate(sum=Sum('order_qty')).order_by('date')
        package = Item.objects.get(pk=product)
        if package.package:
            subtitle = ' - {} {}: {} of {} ea.'.format(package.brand, package.unit, package.package, package.package_qty)
        else:
            subtitle = ' - {} {}'.format(package.brand, package.unit)
            
    else:
        orders = Order.objects.filter(date__range=(start_date, current_date)).values('date')\
            .annotate(sum=Sum('order_qty')).order_by('date')

    if not orders:
        return HttpResponseRedirect(reverse('inventory:nodata'))
    
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


def delete(request):
    if request.method == "POST":
        if request.POST.get('response') == 'yes':
            Order.objects.all().delete()
            Item.objects.all().delete()
            Supplier.objects.all().delete()
            return HttpResponseRedirect(reverse('inventory:delete_occurred'))
        
        return HttpResponseRedirect(reverse('inventory:dashboard'))

    return render(request, 'inventory/delete.html')


def all_data(request):
    if request.method == "POST":
        fileitem = request.FILES['csv_file']
        read_csv(fileitem)
        return HttpResponseRedirect(reverse('inventory:dashboard'))
    return create_csv(all_models=True)
