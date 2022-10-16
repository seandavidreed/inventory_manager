from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'inventory/index.html')

def login(request):
    return render(request, 'inventory/login.html')

def dashboard(request):
    return render(request, 'inventory/dashboard.html')


