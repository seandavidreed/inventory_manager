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
    if request.method == "POST":
        print(request.POST)
        item_id = int(request.POST['id'])
        item_value = request.POST['input']
        item = Item.objects.get(id=item_id)
        order = Order(
            date=datetime.datetime.now(),
            item=item,
            order_qty=item_value
        )
        order.save() 

    item_list = Item.objects.filter(storage__contains='A')
    context = {
        'item_list': item_list,
    }
    return render(request, 'inventory/shed.html', context)


@login_required
def shop(request):
    if request.method == "POST":
        print(request.POST)
        item_id = int(request.POST['id'])
        item_value = request.POST['input']
        item = Item.objects.get(id=item_id)
        order = Order(
            date=datetime.datetime.now(),
            item=item,
            order_qty=item_value
        )
        order.save() 

    item_list = Item.objects.filter(storage__contains='B')
    context = {
        'item_list': item_list,
    }
    return render(request, 'inventory/shop.html', context)


@login_required
def history(request):
    order_list = Order.objects.all().values('date').distinct()
    context = {
        'order_list': order_list,
    }
    return render(request, 'inventory/order-history.html', context)


@login_required
def order(request, order_date):
    orders = Order.objects.filter(date=order_date)
    context = {
        'orders': orders,
    }
    return render(request, 'inventory/order.html', context)

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
