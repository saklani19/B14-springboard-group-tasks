import cv2
import os

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage


# Create your views here.
def home(request):
    return render(request, "home.html")

def loginView(request):
    if(request.user.is_authenticated):
        return render(request,'profile.html')
    if(request.method == "POST"):
        un = request.POST['username']
        pw = request.POST['password']
        '''
        authenticate() is used to check for the values present in the database or not
        if the values are matched, then it will return the username
        if the values are not matched, then it will return as 'None'
        use authenticate(), need to import it from auth package
        '''
        user = authenticate(request,username=un,password=pw)
        if(user is not None):
            return redirect('/profile')
        else:
            msg = 'Invalid Username/Password'
            form = AuthenticationForm(request.POST)
            return render(request,'login.html',{'form':form,'msg':msg})
    else:
        form = AuthenticationForm()
        # used to create a basic login page with username and password
        return render(request,'login.html',{'form':form})

def signup(request):
    if(request.user.is_authenticated):
        return redirect('/profile')
    if(request.method == "POST"):
        form = UserCreationForm(request.POST)
        if(form.is_valid()):
            form.save()
            un = form.cleaned_data.get('username')
            pw = form.cleaned_data.get('password1')
            authenticate(username=un,password=pw)
            return redirect('/login')
    else:
        form = UserCreationForm()
        #UserCreationForm() is used to create a basic registration page with username, password and confirm password
        return render(request,'signup.html',{'form':form})

def profile(request):
    # initialise url variables
    img_url = None
    processed_img_url = None

    if request.method == "POST":
        if request.FILES.get('uploadImage'):
            img_name = request.FILES['uploadImage']
            fs = FileSystemStorage()
            filename = fs.save(img_name.name, img_name)
            img_url = fs.url(filename)

            uploaded_img_path = fs.path(filename)
            processed_img_path = process_image_with_opencv(uploaded_img_path)

            processed_filename = processed_img_path.split('/')[-1]
            processed_fs = FileSystemStorage()
            processed_fs.save(processed_filename, open(processed_img_path, 'rb'))
            processed_img_url = processed_fs.url(processed_filename)

    return render(request, 'profile.html', {'img': img_url, 'processed_img': processed_img_url})

def process_image_with_opencv(input_image_path):
    img = cv2.imread(input_image_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    base_name, ext = os.path.splitext(input_image_path)
    processed_image_path = f"{base_name}_processed{ext}"
    
    cv2.imwrite(processed_image_path, gray_img)

    return processed_image_path