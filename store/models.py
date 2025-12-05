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
    date_modified = models.DateTimeField(auto_now=True)
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
        # Check if image is being updated
        if self.image and hasattr(self.image, 'file'):
            self.compress_image_before_save()
        
        super().save(*args, **kwargs)

    def compress_image_before_save(self):
        """Compress image to under 10MB before saving"""
        try:
            # Open the uploaded image
            img = Image.open(self.image.file)
            
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if too large
            max_size = (1920, 1920)  # Max dimensions
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Compress to reduce file size
            temp_image = BytesIO()
            
            # Start with high quality and reduce until under 9MB
            quality = 85
            max_file_size = 9 * 1024 * 1024  # 9MB (leave 1MB buffer)
            
            while quality > 10:
                temp_image.seek(0)
                temp_image.truncate(0)
                
                # Save with current quality
                img.save(temp_image, format='JPEG', quality=quality, optimize=True)
                
                # Check file size
                if temp_image.tell() <= max_file_size:
                    break
                
                # Reduce quality for next iteration
                quality -= 15
            
            # Replace the image file with compressed version
            self.image.file = temp_image
            self.image.file.seek(0)
            
        except Exception as e:
            print(f"Error compressing image: {e}")
            # Continue with original image if compression fails

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
    sold_out = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    head_sizes = models.ManyToManyField(HeadSize, blank=True)
    allow_custom_size = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def save(self, *args, **kwargs):
        # Compress images before saving
        self.compress_all_images()
        super().save(*args, **kwargs)

    def compress_all_images(self):
        """Compress all product images before upload"""
        image_fields = [
            ('image', self.image),
            ('extra_image1', self.extra_image1),
            ('extra_image2', self.extra_image2)
        ]
        
        for field_name, image_field in image_fields:
            if image_field and hasattr(image_field, 'file'):
                self.compress_product_image(image_field)

    def compress_product_image(self, image_field):
        """Compress a single product image"""
        try:
            # Open the uploaded image
            img = Image.open(image_field.file)
            
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if too large
            max_size = (1920, 1920)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Compress to reduce file size
            temp_image = BytesIO()
            
            quality = 85
            max_file_size = 9 * 1024 * 1024  # 9MB
            
            while quality > 10:
                temp_image.seek(0)
                temp_image.truncate(0)
                
                img.save(temp_image, format='JPEG', quality=quality, optimize=True)
                
                if temp_image.tell() <= max_file_size:
                    break
                
                quality -= 15
            
            # Replace the image file
            image_field.file = temp_image
            image_field.file.seek(0)
            
        except Exception as e:
            print(f"Error compressing product image: {e}")

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