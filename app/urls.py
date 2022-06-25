from django import views
from django.urls import path
from . import views

app_name ="app"
urlpatterns = [
    path('', views.index, name='index'),
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
    path('logout/', views.signout, name='signout'),
    path('details/<int:id>', views.details, name='details'),
    path('page_not_found',views.page_not_found),
    path('profile/<int:id>',views.profile, name='profile'),
    path('changePassword/<int:id>',views.changePassword, name='changePassword'),
    path('addProfile/<int:id>',views.addProfile, name='addProfile'),
    path('user_bids',views.user_bids, name="user_bids"),
    path('khaltiPayment',views.khaltiPayment),
    path('khaltiPaymentVerify',views.khaltiPaymentVerify),
    path('aboutus',views.aboutus),
    path('contact',views.contact),
    path('sellwithus',views.sellwithus),
    path('verygood',views.verygood),
    path('good',views.good),
    path('average',views.average),
    path('bad',views.bad),
    path('verybad',views.verybad),
    
    
    
   

    
]