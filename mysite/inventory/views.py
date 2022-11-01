from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import datetime


from .models import Supplier, Item, Order

# Create your views here.
@login_required
def take_inventory(request):
    if request.path == '/inventory/shed/':
        item_list = Item.objects.filter(storage__contains='A')
    else:
        item_list = Item.objects.filter(storage__contains='B')

    if request.method == "POST":
        for item in item_list:
            item_value = request.POST[str(item.id)]
            order, was_created = Order.objects.get_or_create(date=datetime.datetime.now(), item_id=item.id)
            order.order_qty = item_value
            order.save() 
    return render(request, 'inventory/take-inventory.html', {'item_list': item_list})


@login_required
def history(request):
    order_list = Order.objects.all().values('date').distinct().order_by('-date')
    return render(request, 'inventory/order-history.html', {'order_list': order_list})


@login_required
def order(request, order_date):
    orders = Order.objects.filter(date=order_date)
    return render(request, 'inventory/order.html', {'orders': orders, 'order_date': order_date})


@login_required
def orderfile(request, order_date):
    things = Order.objects.filter(date=order_date)

    # Create Bytestream buffer
    buffer = io.BytesIO()

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # Create a text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)

    textob.setFont("Helvetica", 20)
    textob.textLine("Woodland Espresso Order History")
    textob.setFont("Helvetica", 14)
    textob.textLine(order_date)

    for thing in things:
        textob.textLine(str(thing.item) + str(thing.order_qty))

    p.drawText(textob)
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='order.pdf')


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')
