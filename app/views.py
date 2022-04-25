from this import d
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
from app.models import Bid, Category, Product, UserDetails
from demo import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from . tokens import generate_token
from django.db.models import Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def index(request):
    category = Category.objects.all()
    current_time = tz.now()
    if 'category' in request.GET.keys():
        categoryId = request.GET['category']
        category_products = Product.objects.all().filter(category_id = categoryId)
        cp=Paginator(category_products, 20)
        page_number = request.GET.get('page')
        try:
            page_obj = cp.get_page(page_number)
        except PageNotAnInteger:
            page_obj = cp.page(1)
        except EmptyPage:
            page_obj = cp.page(cp.num_pages)
    else:
        products = Product.objects.all().order_by('-id')
        p=Paginator(products, 20)
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

            #welcome email text
            subject = "Welcome to HAMRO AUCTION SYSTEM"
            message = "Hello... "+ myuser.first_name + "!!\n"+"Thank you for visiting our website\n\n we have sent you a confirmation email, please confirm your email address in order to activate your account.\n\n Thank you\n Krishna"
            from_email = settings.EMAIL_HOST_USER
            to_email_list = [myuser.email]
            send_mail(subject, message, from_email, to_email_list, fail_silently=True)

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
    bids = Bid.objects.all().filter(product=id).order_by('-id')
    bid_count = Bid.objects.all().filter(product=id).count()
    bid_duration = productsDetail.EndingTime - productsDetail.startingTime
    current_time = tz.now()
    
    current_max_bid = Bid.objects.all().filter(product=id).aggregate(Max('bidPrice'))
    try:
        if request.method == "POST":
            if int(request.POST.get('minimum_price')) > int(request.POST.get('bidPrice')):
                messages.error(request,"Bid price should be more than minimum price")
            else:
                if bid_count>0:
                    for i in bids:
                        if i.bidPrice >= int(request.POST.get('bidPrice')):
                            messages.error(request,"Sorry your price must be higher than others")
                            return redirect(f"/details/{id}")
                    
                    for i in bids:
                        if i.bidPrice < int(request.POST.get('bidPrice')):
                            bid = Bid(time = datetime.now().strftime('%H:%M:%S'),bidPrice=request.POST.get('bidPrice'),user=request.user,product=Product.objects.get(id=request.POST.get('product_id')))
                            bid.save()
                            messages.success(request, "you Bid successfully.")
                            return redirect(f"/details/{id}")
                        # else:
                        #     messages.error(request,"Sorry your price must be higher than others")
                        #     return redirect(f"/details/{id}")
                        
                    
                else:
                    bid = Bid(time = datetime.now().strftime('%H:%M:%S'),bidPrice=request.POST.get('bidPrice'),user=request.user,product=Product.objects.get(id=request.POST.get('product_id')))
                    bid.save()
                    messages.success(request, "you successfully.")
                    return redirect(f"/details/{id}")
                    
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
            
        
           
    
    