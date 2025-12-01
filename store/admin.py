from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile, ContactMessage, HeadSize, Wishlist
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Wishlist)

# Register HeadSize model
@admin.register(HeadSize)
class HeadSizeAdmin(admin.ModelAdmin):
    list_display = ['cm', 'inches', 'standard_size']
    list_filter = ['standard_size']
    search_fields = ['cm', 'inches', 'standard_size']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name','email','created_at','read')
    list_filter = ('read','created_at')
    search_fields = ('name','email','message')

# Mix profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

# Unregister the old way
admin.site.unregister(User)

# Re-Register the new way
admin.site.register(User, UserAdmin)