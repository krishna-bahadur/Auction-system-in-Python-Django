from msilib.schema import Class
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe




class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="media/product")
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    actualAmount = models.IntegerField()
    startingTime = models.DateTimeField()
    EndingTime = models.DateTimeField()
    post_view =models.IntegerField(default=0,null=True,blank=True)
  
    

    def admin_photo(self):
        return mark_safe('<img src="{}" width="50px" height="50px"  />'.format(self.image.url))
    admin_photo.short_description = 'Image'
    admin_photo.allow_tags = True
    
    def __str__(self):
        return self.title

  

    
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to="media/productImages")
    
    def admin_images(self):
        return mark_safe('<img src="{}" width="50px" height="50px" />'.format(self.images.url))
    admin_images.short_description = 'Image'
    admin_images.allow_tags = True
    
    def __str__(self):
        return self.product.title
    
    
class Bid(models.Model):
    time = models.TimeField()
    bidPrice =models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.BooleanField(blank=True,null=True)
    payment = models.BooleanField(blank=True,null=True)
    
   
    
class UserDetails(models.Model):
    profilePicture = models.ImageField(upload_to="media/profile")
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    
    def user_profile(self):
        return mark_safe('<img src="{}" width="50px" height="50px" />'.format(self.profilePicture.url))
    user_profile.short_description = 'User Profile'
    user_profile.allow_tags = True
    
    
class Payment(models.Model):
    user = models.CharField(max_length=100,blank=True, null=True)
    token = models.CharField(max_length=100,blank=True, null=True)
    amount = models.CharField(max_length=100,blank=True, null=True)
    product = models.CharField(max_length=100,blank=True, null=True)
    paymentId = models.CharField(max_length=100,blank=True, null=True)
    
    def __str__(self):
        return self.product
    
    
class Message(models.Model):
    fullname = models.CharField(max_length=100,blank=True, null=True)
    email = models.CharField(max_length=100,blank=True, null=True)
    message = models.CharField(max_length=500,blank=True, null=True)
    
    def __str__(self):
        return self.fullname
    
    
class Seller(models.Model):
    fullname = models.CharField(max_length=100,blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    
    def __str__(self):
        return self.fullname

class Rating(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    rate = models.IntegerField(default=0)