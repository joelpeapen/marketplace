from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def about(request):
    return render(request, "about.html")

def add(request):
    # get data from reqeust
    n1 = int(request.GET.get('num1', 0))
    n2 = int(request.GET.get('num2', 0))
    return render(request, "add.html", {"sum": n1 + n2 })
