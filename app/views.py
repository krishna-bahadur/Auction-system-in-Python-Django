from audioop import add
from distutils.log import error
from email import message
from itertools import product
from sre_constants import SUCCESS
from this import d
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone as tz
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login, logout
from datetime import date, datetime
from app.forms import BidForms
from app.models import Bid, Category, Message, Payment, Product, Rating, Seller, UserDetails
from demo import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from . tokens import generate_token
from django.db.models import Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import time

def index(request):
    category = Category.objects.all()
    current_time = tz.now()
    if 'category' in request.GET.keys():
        categoryId = request.GET['category']
        category_products = Product.objects.all().filter(category_id = categoryId).order_by('-id')
        cp=Paginator(category_products, 31)
        page_number = request.GET.get('page')
        try:
            page_obj = cp.get_page(page_number)
        except PageNotAnInteger:
            page_obj = cp.page(1)
        except EmptyPage:
            page_obj = cp.page(cp.num_pages)
    else:
        products = Product.objects.all().order_by('-id')
        p=Paginator(products, 31)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
     
    return render(request,"index.html", {'products':page_obj, 'category':category,'current_time':current_time,});

def details(request):
    
    return render(request, "details.html")


def signin(request):
    if(request.method == "POST"):
        username=request.POST['username']
        password=request.POST['password']
        
        error_message=None
        
        if not username:
            error_message = "username is required."
        elif not password:
            error_message = "Password is required."
            
        if not error_message:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "you are logged in successfully.")
                # return render(request, 'index.html', {'fname':fname})
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password !")
                return redirect('/signin')
        else:
            return render(request, "signin.html", {'error': error_message})
    return render(request, 'signin.html')

def signup(request):
    error_message=None
    if(request.method == "POST"):
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
        conpassword=request.POST['conpassword']

        
        if not first_name:
            error_message = "First name is required."
        else:
            if first_name.isnumeric():
                error_message = "First name only contains alphabet only."
            else:
                if not last_name:
                    error_message = "Last name is required."
                else:
                    if last_name.isnumeric():
                        error_message = "Last name only contains alphabet only."
                    else:
                        if not email:
                            error_message = "Email is required."
                        else:
                            if not username:
                                error_message = "Username is required."
                            else:
                                if not password:
                                    error_message = "Password is required."
                                else:
                                    if len(password) < 5:
                                        error_message = "password must contain atleast 5 letters."
                                    else:
                                        if not conpassword:
                                            error_message = "Confirmation password is required."
                           
                
        if not error_message:
            if User.objects.filter(username=username):
                messages.error(request, "Username already exists ! Please try some other username.")
                return redirect('/signup')

            if User.objects.filter(email=email):
                messages.error(request, "Email already registered !")
                return redirect('/signup')
            
            if password != conpassword:
                messages.error(request, "Password didn't match !")
                return redirect('/signup')

            if not username.isalnum():
                messages.error(request, "Username must be alpha-numeric")
                return redirect('/signup')
        
            myuser = User.objects.create_user(username, email, password)
            myuser.first_name = first_name
            myuser.last_name = last_name

            myuser.is_active = False
            myuser.save();

            messages.success(request,"Your account has been successfully created. We have sent you a confirmation email, Please confirm your accoount.")

            #Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email for Login!!"
            message2 = render_to_string('email_confirmation.html',{
                'name': myuser.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': generate_token.make_token(myuser)
            })
            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
            )
            email.fail_silently = True
            email.send()
            
            return redirect('/signin')
        else:
            return render(request, "signup.html",{'error': error_message})
        
    return render(request, "signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('/')
    else:
        return render(request,'activation_failed.html')




def signout(request):
    logout(request)
    messages.success(request,"Logout successfully.")
    return redirect('/signin')

def details(request, id):
    
    productsDetail = Product.objects.get(id=id)
    productsDetail.post_view = productsDetail.post_view + 1
    productsDetail.save()
    bids = Bid.objects.all().filter(product=id).order_by('-id')
    bid_count = Bid.objects.all().filter(product=id).count()
    current_time = tz.now()
    current_max_bid = Bid.objects.all().filter(product=id).aggregate(Max('bidPrice'))
    
    
        
    #winner of the product by using latest bid and send email
    if productsDetail.EndingTime == current_time:
        latest_bid = Bid.objects.filter(product=id).order_by('-id')[0]
        latest_bid.status = True
        latest_bid.save()
        subject = "Welcome to HAMRO AUCTION SYSTEM"
        message = "Hello... "+latest_bid.user.first_name+" You are the winner of "+latest_bid.product.title+" product you have bid !! check your profile now\nThank you..\nFrom auction system"
        from_email = settings.EMAIL_HOST_USER
        to_email_list = [latest_bid.user.email]
        send_mail(subject, message, from_email, to_email_list, fail_silently=True)

    
    try:
        if request.method == "POST":
            if int(request.POST.get('minimum_price')) >= int(request.POST.get('bidPrice')):
                messages.error(request,"Bid price should be more than minimum price")
            else:
                if bid_count>0:
                    for i in bids:
                        if i.bidPrice >= int(request.POST.get('bidPrice')):
                            messages.error(request,"Sorry your price must be higher than others")
                            return redirect(f"/details/{id}")
                    
                    for i in bids:
                        if i.bidPrice <= int(request.POST.get('bidPrice')):
                            bid = Bid(time = datetime.now().strftime('%H:%M:%S'),bidPrice=request.POST.get('bidPrice'),user=request.user,product=Product.objects.get(id=request.POST.get('product_id')))
                            current_bid = Bid.objects.filter(product=id).order_by('-id')[0]
                            subject = "Welcome to HAMRO AUCTION SYSTEM"
                            message = "Hello... "+current_bid.user.first_name+" Some other user has bid more than your price in the product you bid\nLets bid higher price\nThank you..\nFrom auction system"
                            from_email = settings.EMAIL_HOST_USER
                            to_email_list = [current_bid.user.email]
                            send_mail(subject, message, from_email, to_email_list, fail_silently=True)  
                            bid.save()
                            messages.success(request, "you Bid successfully.")
                            return redirect(f"/details/{id}")
                else:
                    bid = Bid(time = datetime.now().strftime('%H:%M:%S'),bidPrice=request.POST.get('bidPrice'),user=request.user,product=Product.objects.get(id=request.POST.get('product_id')))
                    bid.save()
                    messages.success(request, "you Bid successfully.")
                    return redirect(f"/details/{id}")
          
        if Rating.objects.filter(product=id):
            rating = Rating.objects.get(product=id)
            return render(request, "details.html" ,
                      {'productsDetail':productsDetail,
                       'bids':bids,
                       'current_max_bid':current_max_bid,
                       'current_time':current_time,
                       'rating':rating
                       })
        else:
            return render(request, "details.html" ,
                      {'productsDetail':productsDetail,
                       'bids':bids,
                       'current_max_bid':current_max_bid,
                       'current_time':current_time,
                       
                       })
        
    except Product.DoesNotExist:
        return render(request, '404.html')
def page_not_found(request):
    return render(request,'404.html') 

def profile(request, id):
    u = User.objects.get(id=id)
    if UserDetails.objects.filter(user=request.user):
        user_img = UserDetails.objects.get(user=request.user)
        return render(request,'profile.html',{'user':u, 'user_img':user_img})
    else:
         return render(request,'profile.html',{'user':u})
   

def addProfile(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST" and request.FILES['profilePicture']:
        img = request.FILES['profilePicture']
        userDetails = UserDetails(profilePicture=img, user=request.user)
        userDetails.save()
        messages.success(request,"Profile picture added successsfully")
        return redirect(f"/profile/{id}")
    


def changePassword(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.set_password(request.POST['newPassword'])
        user.save()
        messages.success(request,"Password change successsfully")
        return redirect('/signin')
            
          
def user_bids(request):
    User_bid = Bid.objects.filter(user = request.user)
    return render(request,'user_bids.html',{'User_bid':User_bid})

    
    
def khaltiPayment(request):
    if request.method == "POST":
        id = request.POST['id']
        User_bid = Bid.objects.get(id = id)
        user_detail = UserDetails.objects.get(user=request.user)
        user_detail.phone = request.POST['phone']
        user_detail.address= request.POST['address']
        user_detail.save()
        return render(request,"KhaltiPayment.html",{'p':User_bid})
    
    
def khaltiPaymentVerify(request):
    token =request.GET.get("token")
    amount = request.GET.get("amount")
    product = request.GET.get("product")
    id = request.GET.get("product_id")
    print(token, amount, product)
    int_amount = int(amount);
    a = int_amount/100
    actual_amount = str(a)
    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        "token": token,
        "amount": amount,
    }
    headers = {
        "Authorization": "Key test_secret_key_97a97fe93bff4a9ea39cb63ba22950cf"
    }
    response = requests.post(url, payload, headers = headers)
    resp_dict = response.json()
    if resp_dict.get('idx'):
        success = True
        
        #email notification for payment
        subject = "Payment Success!"
        message = "Hello... "+request.user.first_name+" Your payment is successfull of product \n\nDetails\nId: "+resp_dict.get('idx')+" \nProduct Name "+product+"\nAmount Rs "+actual_amount+"\nToken no: "+token+"\n\n Thank you for visiting Hamro Auction System..\nFrom Krishna Bk"
        from_email = settings.EMAIL_HOST_USER
        to_email_list = [request.user.email]
        send_mail(subject, message, from_email, to_email_list, fail_silently=True)
        
        
        bid = Bid.objects.get(id=id)
        bid.payment = True
        bid.save()
        payment = Payment(user = request.user,token = token,amount = actual_amount, product = product, paymentId=resp_dict.get('idx'))
        payment.save()
        # if true then save the data as it is paid
    else:
        success = False
    data ={
        "success" : success
    }
    return JsonResponse(data)

def aboutus(request):
    return render(request,'about.html')

def contact(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        mes = request.POST['message']
        obj = Message(fullname=fullname,email=email,message=mes)
        obj.save()
        messages.success(request, 'You message is successfully submit')
        return redirect('/contact')
    return render(request,'contact.html')

def sellwithus(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        username = request.POST['username']
        description = request.POST['description']
        user = request.user.username
        if user == username:
            seller = Seller(fullname=fullname,user=request.user,description=description)
            seller.save()
            messages.success(request, "You information is submitted.")
            return redirect('/sellwithus')
        else:
            messages.error(request,"Please provide your correct username.")
            return redirect('/sellwithus')
        
    return render(request,'sellwithus.html')

def likes(request, id):
    id=request.POST['id']
    post = get_object_or_404(Product, id=id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect('/')
    
def verygood(request):
    if request.method=="POST":
        id=request.POST['id']
        p=Product.objects.get(id=id)
        ratings = Rating(user=request.user,product=p,rate=5)
        ratings.save()
        messages.success(request,"Thanks for your ratings.")
        return redirect(f"/details/{id}")
    
def good(request):
    if request.method=="POST":
        id=request.POST['id']
        p=Product.objects.get(id=id)
        ratings = Rating(user=request.user,product=p,rate=4)
        ratings.save()
        messages.success(request,"Thanks for your ratings.")
        return redirect(f"/details/{id}")
    
def average(request):
    if request.method=="POST":
        id=request.POST['id']
        p=Product.objects.get(id=id)
        ratings = Rating(user=request.user,product=p,rate=3)
        ratings.save()
        messages.success(request,"Thanks for your ratings.")
        return redirect(f"/details/{id}")
    
def bad(request):
    if request.method=="POST":
        id=request.POST['id']
        p=Product.objects.get(id=id)
        ratings = Rating(user=request.user,product=p,rate=2)
        ratings.save()
        messages.success(request,"Thanks for your ratings.")
        return redirect(f"/details/{id}")
    
def verybad(request):
    if request.method=="POST":
        id=request.POST['id']
        p=Product.objects.get(id=id)
        ratings = Rating(user=request.user,product=p,rate=1)
        ratings.save()
        messages.success(request,"Thanks for your ratings.")
        return redirect(f"/details/{id}")
    