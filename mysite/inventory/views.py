from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from django.http import HttpResponseRedirect
import datetime


from .models import Supplier, Item, Order

# Create your views here.
@login_required
def shed(request):
    item_list = Item.objects.filter(storage__contains='A')
    if request.method == "POST":
        for item in item_list:
            item_value = request.POST[str(item.id)]
            order, was_created = Order.objects.get_or_create(date=datetime.datetime.now(), item_id=item.id)
            order.order_qty = item_value
            order.save() 
    return render(request, 'inventory/shed.html', {'item_list': item_list})


@login_required
def shop(request):
    item_list = Item.objects.filter(storage__contains='B')
    if request.method == "POST":
        for item in item_list:
            item_value = request.POST[str(item.id)]
            order, was_created = Order.objects.get_or_create(date=datetime.datetime.now(), item_id=item.id)
            order.order_qty = item_value
            order.save() 
    return render(request, 'inventory/shop.html', {'item_list': item_list})


@login_required
def history(request):
    order_list = Order.objects.all().values('date').distinct().order_by('-date')
    return render(request, 'inventory/order-history.html', {'order_list': order_list})


@login_required
def order(request, order_date):
    orders = Order.objects.filter(date=order_date)
    return render(request, 'inventory/order.html', {'orders': orders})


@login_required
def orderfile(request):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    p.drawString(100, 100, "Hello, world.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='order.pdf')


def login(request):
    return render(request, 'inventory/login.html')


def dashboard(request):
    return render(request, 'inventory/dashboard.html')

# def temp(request):
#     submitted = False
#     if request.method == "POST":
#         form = TakeInventory(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/inventory/temp?submitted=True')
#     else:
#         form = TakeInventory
#         if 'submitted' in request.GET:
#             submitted = True
#     return render(request, 'inventory/temp.html', {'form': form, 'submitted': submitted})
