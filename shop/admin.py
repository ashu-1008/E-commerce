from django.contrib import admin

# Register your models here.
from .models import Product, CustomerContact, Orders, OrderUpdate

admin.site.register(Product)
admin.site.register(CustomerContact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)

