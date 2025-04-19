from django.contrib import admin

from .models import Farmer, Product, FarmerTransaction,Community,Cart,Payment,Vendor,FarmerScheme
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'box')
    search_fields = ('name__username', 'box')


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('farm_name', 'user', 'contact_number', 'joined_on')
    search_fields = ('farm_name', 'user__username', 'contact_number')
    list_filter = ('joined_on',)
    readonly_fields = ('joined_on',)
    
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'user', 'contact_number', 'joined_on')
    search_fields = ('vendor_name', 'user__username', 'contact_number')
    list_filter = ('joined_on',)
    readonly_fields = ('joined_on',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price_per_unit', 'quantity_available', 'listed_on')
    list_filter = ('category', 'listed_on')
    search_fields = ('name', 'farmer__farm_name', 'category')
    readonly_fields = ('listed_on',)

@admin.register(FarmerTransaction)
class FarmerTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'farmer', 'product', 'quantity_sold', 'total_amount', 'payment_status', 'transaction_date')
    list_filter = ('payment_status', 'transaction_date')
    search_fields = ('transaction_id', 'farmer__farm_name', 'product__name', 'buyer_name')
    readonly_fields = ('transaction_date',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_on')
    list_filter = ('added_on',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_on',)

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'
    
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "order_id", "payment_id", "amount", "status", "created_at")
    list_filter = ("status", "created_at",'user')
    search_fields = ("order_id", "payment_id", "user__username", "user__email", "user__parent__full_name")  
    
@admin.register(FarmerScheme)
class FarmerSchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'launch_date')
    list_filter = ('state', 'launch_date')
    search_fields = ('name', 'description', 'eligibility_criteria', 'benefits')
    ordering = ('launch_date',)

    def get_state_display(self, obj):
        return obj.get_state_display()
    get_state_display.short_description = 'State'
    
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
