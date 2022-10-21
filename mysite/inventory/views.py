from django.shortcuts import render

from .models import Item

# Create your views here.
def index(request):
    item_list = Item.objects.all()
    for item in item_list:
        setattr(item, 'difference', item.par - item.current_qty)
    context = {
        'item_list': item_list,
    }
    return render(request, 'inventory/index.html', context)

def login(request):
    return render(request, 'inventory/login.html')

def dashboard(request):
    return render(request, 'inventory/dashboard.html')


