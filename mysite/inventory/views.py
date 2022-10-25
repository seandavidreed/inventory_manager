from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime


from .models import Supplier, Item, Order

# Create your views here.
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
