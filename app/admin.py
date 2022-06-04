from django.db import models
from django.contrib import admin
from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver
from app.models import Category, Product, ProductImages, Bid, UserDetails, Payment
import os
from tinymce.widgets import TinyMCE
from tinymce.models import HTMLField 

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_photo','actualAmount','category')
    #filter product by category and starting time
    list_filter = ('category','startingTime')
    list_per_page = 20
    description =  HTMLField()
    
    formfield_overrides = {
    models.TextField: {'widget': TinyMCE()}
    }
   
    
    #delete image from folder when deleting post
    @receiver(pre_delete, sender=Product)
    def post_save_image(sender, instance, *args, **kwargs):
        try:
            instance.image.delete(save=False)
        except:
            pass
        
    # update image in the folder while updating the post
    @receiver(pre_save, sender=Product)
    def pre_save_image(sender, instance, *args, **kwargs):
        try:
            old_img = instance.__class__.objects.get(id=instance.id).image.path
            try:
                new_img = instance.image.path
            except:
                new_img = None
            if new_img != old_img:
                if os.path.exists(old_img):
                    os.remove(old_img)
        except:
            pass

class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'admin_images')
    #pagination with 15 item in one page
    list_per_page = 15
    
    #delete image from folder when deleting post
    @receiver(pre_delete, sender=ProductImages)
    def post_save_image(sender, instance, *args, **kwargs):
        try:
            instance.images.delete(save=False)
        except:
            pass
    # update image in the folder while updating the post  
    @receiver(pre_save, sender=ProductImages)
    def pre_save_image(sender, instance, *args, **kwargs):
        try:
            old_img = instance.__class__.objects.get(id=instance.id).images.path
            try:
                new_img = instance.images.path
            except:
                new_img = None
            if new_img != old_img:
                if os.path.exists(old_img):
                    os.remove(old_img)
        except:
            pass
    
class BidAdmin(admin.ModelAdmin):
    list_display = ('product', 'user','bidPrice','time','status','payment')
    search_fields = ['product__title']
    list_per_page = 20
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ['user','user_profile','phone','address']
    
    #delete image from folder when deleting post
    @receiver(pre_delete, sender=UserDetails)
    def post_save_image(sender, instance, *args, **kwargs):
        try:
            instance.profilePicture.delete(save=False)
        except:
            pass
        
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('paymentId','product', 'user','amount','token')   

admin.site.register(Payment,PaymentAdmin)    
admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImages,ProductImagesAdmin)
admin.site.register(Bid,BidAdmin)
admin.site.register(UserDetails, UserDetailsAdmin)