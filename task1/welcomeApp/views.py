from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")

def loginView(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')