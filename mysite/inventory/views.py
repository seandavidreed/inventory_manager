from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.core.mail import EmailMessage
from django.urls import reverse
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


def createPDF():
    # Fetch database objects by date
    things = Order.objects.filter(date=datetime.datetime.now(), item__supplier__name='Cash and Carry')

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for thing in things:
        if b is True:
            # Create a text object
            textob = p.beginText()
            textob.setTextOrigin(inch, inch)

            # Create Letterhead
            textob.setFont("Courier", 18)
            textob.textLine("Woodland Espresso")
            p.setLineWidth(0.05*inch)
            p.line(1*inch, 1.1*inch, 7.5*inch, 1.1*inch)

            # Display order date
            textob.setFont("Courier", 12)
            textob.textLine("Order Placed: " + str(datetime.datetime.now()))
            textob.textLine()

            # Table Headers (currently hard-coded: probably should change)
            textob.setFont("Courier-Bold", 12)
            textob.textOut("Item")
            textob.moveCursor(5*inch, 0)
            textob.textOut("Order Qty")
            textob.moveCursor(-5*inch, 0)
            textob.textLine()
            b = False

        # Populate document with data from database
        textob.setFont("Courier", 12)
        textob.textOut(str(thing.item))
        textob.moveCursor(5*inch, 0)
        textob.textOut(str(thing.order_qty))
        textob.moveCursor(-5*inch, 0)
        textob.textLine()
        if textob.getCursor()[1] >= 712:
            b = True
            p.drawText(textob)
            p.showPage()

    # Render PDF document
    p.drawText(textob)
    p.showPage()
    p.save()

    buffer.seek(0)
    pdf = buffer.getvalue()
    return pdf


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
def history(request):
    order_list = Order.objects.all().values('date').distinct().order_by('-date')
    return render(request, 'inventory/order-history.html', {'order_list': order_list})


@login_required
def order(request, order_date):
    orders = Order.objects.filter(date=order_date)
    return render(request, 'inventory/order.html', {'orders': orders, 'order_date': order_date})


@login_required
def orderfile(request, order_date):
    # Fetch database objects by date
    things = Order.objects.filter(date=order_date)

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for thing in things:
        if b is True:
            # Create a text object
            textob = p.beginText()
            textob.setTextOrigin(inch, inch)

            # Create Letterhead
            textob.setFont("Courier", 18)
            textob.textLine("Woodland Espresso")
            p.setLineWidth(0.05*inch)
            p.line(1*inch, 1.1*inch, 7.5*inch, 1.1*inch)

            # Display order date
            textob.setFont("Courier", 12)
            textob.textLine("Order Placed: " + order_date)
            textob.textLine()

            # Table Headers (currently hard-coded: probably should change)
            textob.setFont("Courier-Bold", 12)
            textob.textOut("Item")
            textob.moveCursor(5*inch, 0)
            textob.textOut("Order Qty")
            textob.moveCursor(-5*inch, 0)
            textob.textLine()
            b = False

        # Populate document with data from database
        textob.setFont("Courier", 12)
        textob.textOut(str(thing.item))
        textob.moveCursor(5*inch, 0)
        textob.textOut(str(thing.order_qty))
        textob.moveCursor(-5*inch, 0)
        textob.textLine()
        if textob.getCursor()[1] >= 712:
            b = True
            p.drawText(textob)
            p.showPage()

    # Render PDF document
    p.drawText(textob)
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='order.pdf')


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')
