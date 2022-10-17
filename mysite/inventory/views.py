from django.shortcuts import render

from .models import Item

# Create your views here.
def index(request):
    item_list = Item.objects.all()
    context = {
        'item_list': item_list,
    }
    return render(request, 'inventory/index.html', context)

def login(request):
    return render(request, 'inventory/login.html')

def dashboard(request):
    return render(request, 'inventory/dashboard.html')


