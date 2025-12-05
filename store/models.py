from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
from PIL import Image
from io import BytesIO
import cloudinary.uploader


# Create Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)  # FIXED: removed User parameter
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()


post_save.connect(create_profile, sender=User)


# Categories of Products
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads/category/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Save first to get the image
        super().save(*args, **kwargs)
        
        # Resize image after save (works with Cloudinary)
        if self.image:
            try:
                self.resize_and_upload_image()
            except Exception as e:
                print(f"Error resizing category image: {e}")

    def resize_and_upload_image(self):
        """Resize and upload image for Cloudinary storage"""
        try:
            # Open image from the uploaded file
            img = Image.open(self.image)
            
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize
            max_size = (1080, 1080)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to memory
            temp_image = BytesIO()
            img.save(temp_image, format='JPEG', quality=70, optimize=True)
            temp_image.seek(0)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                temp_image,
                folder="categories/",
                public_id=f"category_{self.id}",
                overwrite=True,
                resource_type="image"
            )
            
            # Note: With Cloudinary, the image is already uploaded
            # We don't need to update the field as Cloudinary handles storage
            
        except Exception as e:
            print(f"Error in resize_and_upload_image for category: {e}")
            # Don't break if resizing fails

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


# Customers
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# Head Size Model
class HeadSize(models.Model):
    cm = models.CharField(max_length=10)
    inches = models.CharField(max_length=20)
    standard_size = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.cm} | {self.inches} | {self.standard_size}"


# All of our Products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.TextField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    extra_image1 = models.ImageField(upload_to='uploads/product/', blank=True, null=True)
    extra_image2 = models.ImageField(upload_to='uploads/product/', blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    # Product is sold out
    sold_out = models.BooleanField(default=False)
    # Product is unique
    is_unique = models.BooleanField(default=False)
    # Head sizes for products that require size selection
    head_sizes = models.ManyToManyField(HeadSize, blank=True)
    allow_custom_size = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def save(self, *args, **kwargs):
        # Save first
        super().save(*args, **kwargs)
        
        # Resize images after save
        self.resize_all_images()
    
    def resize_all_images(self):
        """Resize all product images"""
        image_fields = [self.image]
        if self.extra_image1:
            image_fields.append(self.extra_image1)
        if self.extra_image2:
            image_fields.append(self.extra_image2)
        
        for i, image_field in enumerate(image_fields):
            if image_field:
                try:
                    self.resize_product_image(image_field, i)
                except Exception as e:
                    print(f"Error resizing product image {i}: {e}")
    
    def resize_product_image(self, image_field, index=0):
        """Resize and upload a single product image"""
        try:
            # Open image
            img = Image.open(image_field)
            
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize
            max_size = (1080, 1080)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to memory
            temp_image = BytesIO()
            img.save(temp_image, format='JPEG', quality=70, optimize=True)
            temp_image.seek(0)
            
            # Upload to Cloudinary with appropriate folder
            folder = "products/"
            public_id = f"product_{self.id}"
            if index > 0:
                public_id = f"product_{self.id}_extra_{index}"
            
            result = cloudinary.uploader.upload(
                temp_image,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
        except Exception as e:
            print(f"Error in resize_product_image: {e}")

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.created_at:%Y-%m-%d %H:%M}"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.product)


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, blank=True, related_name='wishlisted_by')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist({self.user.username})"