import cv2
import os
import numpy as np
import joblib

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage

model = joblib.load(os.path.join(os.path.dirname(__file__), 'svm_rbf_model_svc.joblib'))
# label_encoder = joblib.load(os.path.join(os.path.dirname(__file__), 'label_encoder.joblib'))  # Load label encoder


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
    img_url = None
    result1 = None
    result2 = None
    
    if(request.method=="POST"):
        if(request.FILES.get('uploadImage')):
            img_name = request.FILES['uploadImage']
            # create a variable for our FileSystem package
            fs = FileSystemStorage()
            filename = fs.save(img_name.name,img_name)
            #urls
            img_url = fs.url(filename)
            #find the path of the image
            img_path = fs.path(filename)
 
            #start implementing the opencv condition
            img = cv2.imread(img_path,cv2.IMREAD_COLOR)
            # Convert to grayscale (single channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #resize the image for a constant use
            img = cv2.resize(img,(64,64))
            #flatten the image for the better clear shape of the disease spread on the skin
            img = img.flatten()
            #using the normalization predefined function to find the value
            img = np.expand_dims(img,axis=0)
 
            #we sill start executing with our model
            predict = model.predict(img)[0]
            
            ''''''
            skin_disease_names = ['Cellulitis','Impetigo','Athlete Foot','Nail Fungus','Ringworm','Cutaneous Larva Migrans','Chickenpox','Shingles']
            # diagnosis = ['']
 
            result1 = skin_disease_names[predict]
            # result2 = diagnosis[predict]
 
    return render(request,'profile.html',{'img':img_url,'obj1':result1,'obj2':result2})
