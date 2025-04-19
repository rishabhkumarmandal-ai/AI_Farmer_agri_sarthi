from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
# Get the user model
User = get_user_model()  # Use get_user_model() to support custom user models

class Community(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to User model
    box = models.TextField(max_length=500)  # TextField for community box

    def __str__(self):
        return self.name.username  # Optional: return a string representation



User = get_user_model()

# Helper Choices
TRANSACTION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
]
# Category Choices
PRODUCT_CATEGORY_CHOICES = [
    ('FRUIT', 'Fruit'),
    ('VEGETABLE', 'Vegetable'),
    ('GRAIN', 'Grain'),
    ('PULSE', 'Pulse'),
    ('SPICE', 'Spice'),
    ('DAIRY', 'Dairy'),
    ('HERB', 'Herb'),
    ('TUBER', 'Tuber'),
    ('FLOWER', 'Flower'),
    ('OILSEED', 'Oilseed'),
    ('NUT', 'Nut'),
    ('OTHER', 'Other'),
]

# Farmer Profile
class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    profile_image = models.ImageField(upload_to='farmer_profiles/', blank=True, null=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.farm_name

# Product listed by Farmer
class Product(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=PRODUCT_CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    unit = models.CharField(max_length=50, help_text='e.g. kg, litre, bundle')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    listed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.farmer.farm_name}"

# Transaction Details for Farmer Sales
class FarmerTransaction(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    buyer_name = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Txn #{self.id} - {self.product.name} ({self.farmer.farm_name})"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate entries for same product

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.user.username}'s cart"

    @property
    def total_price(self):
        return self.quantity * self.product.price_per_unit
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=50, default="Created")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    receipt_pdf = models.FileField(upload_to="receipts/", blank=True, null=True)

    def __str__(self):
        return f"Payment {self.order_id} - {self.status}"
    
# Vendor Profile
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    profile_image = models.ImageField(upload_to='farmer_profiles/', blank=True, null=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.farm_name
    

STATE_CHOICES = [
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CG', 'Chhattisgarh'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JK', 'Jammu and Kashmir'),
    ('JH', 'Jharkhand'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('MP', 'Madhya Pradesh'),
    ('MH', 'Maharashtra'),
    ('MN', 'Manipur'),
    ('ML', 'Meghalaya'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OD', 'Odisha'),
    ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TS', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
    ('IN', 'India'),
]

class FarmerScheme(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    launch_date = models.DateField()
    eligibility_criteria = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_state_display()})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Processing")

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    @property
    def total(self):
        return self.quantity * self.price