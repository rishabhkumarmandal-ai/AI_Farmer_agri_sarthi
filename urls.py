# app/urls.py
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_page, name='upload_page'), 
    path('predict/', views.predict_image, name='predict_image'),  
    path('solution/', views.SolutionView, name='solution'),
    
    path("signup/", views.signup_view, name="signup"),  
    path("home/", views.login_view, name="login"), 
    path('auth/', include('social_django.urls', namespace='social')), 
    path("", views.logout_view, name="logout"),
    
    
    path("plant/questions/", views.ask_plant_questions, name="ask_plant_questions"),
    path("plant/solution/", views.plant_solution, name="plant_solution"),
    path("farmer/orders/", views.staff_orders_view, name="farmer_orders"),
    path('farmer/chatbot',views.chat_view,name='chatbot'),
    path('farmer/weather',views.weather_view,name="weather"),
    path('schemes/', views.scheme_list, name='scheme_list'),
    path("community/", views.CommunityView, name="community"),
    path('remove/<int:id>/', views.remove, name='delete'),
    path("farmer/",views.farmer_view,name="farmer_homepage"),
    path("product/",views.farmer_productlist_view,name="product_list"),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('farmer/profile/', views.farmer_profile_view, name='farmer_profile'),
    path('profile/edit/', views.edit_farmer_profile, name='edit_farmer_profile'),
    
    
    
    path('my-orders/', views.order_list, name='order_list'),
    path('vendor/register/', views.register_vendor_profile, name='register_vendor_profile'),
    path("vendor/",views.vendor_homepage,name="vendor_homepage"),
    path('vendor/product_list', views.product_list_view, name='vendor_product_list'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('vendor/profile/', views.vendor_profile_view, name='vendor_profile'),
    path('vendor/profile/edit/', views.edit_vendor_profile, name='edit_vendor_profile'),
    
    path("pay/", views.create_order, name="pay"),
    path("payment-success/", views.payment_success, name="payment_success"),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    