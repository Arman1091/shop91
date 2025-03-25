# urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('checkout/', views.checkout, name="checkout"),
    path('checkout/checkout-inscription', views.checkout_inscription, name='checkout_inscription'),
    path('checkout/checkout-connexion', views.checkout_connexion, name='checkout_connexion'),
    path('checkout/checkout-address', views.checkout_address, name='checkout_adresses'),
    path('checkout/checkout-payment', views.checkout_payment, name='checkout_payment'),
    path('checkout/livraison/', views.checkout_livraison, name='checkout_livraison'),
    path('complete-profile/', views.complete_profile, name="complete_profile"),
    path('', views.home, name="home"),
    path('categories/', views.all_categories, name='all_categories'),
    path('test/', views.test, name="test"),
    path('test2/', views.test2, name="test2"),
    path('<slug:category_slug>/<slug:activity_slug>-<int:product_id>/editeur/', views.editeur, name='editeur'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('registration/', views.CustomerRegistrationView.as_view(), name="customerregistration"),
    path('login/', views.CustomLoginView.as_view(template_name="registrations/login.html", authentication_form=LoginForm), name="login"),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name="registrations/changepassword.html", form_class=MyPasswordChangeForm, success_url='/passwordchangedone'), name="passwordchange"),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name="registrations/passwordchangedone.html"), name="passwordchangedone"),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="registrations/password_reset.html", form_class=MyPasswordResetForm), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registrations/password_reset_done.html"), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registrations/password_reset_confirm.html", form_class=MySetPasswordForm), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registrations/password_reset_complete.html"), name="password_reset_complete"),
    path("customize/<int:product_id>/", views.customize_product, name="customize_product"),
    path("customization-success/<int:customized_product_id>/", views.customization_success, name="customization_success"),
    path("wishlist/add/<int:customized_product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("cart/add/<int:customized_product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("wishlist/", views.view_wishlist, name="view_wishlist"),  # Nouvelle route pour la wishlist
    path("success/", views.success, name="success"),
    path("customization-success-temp/", views.customization_success_temp, name="customization_success_temp"),
    path("cookie-policy/", views.cookie_policy, name="cookie_policy"),
    path("set-cookie-consent/", views.set_cookie_consent, name="set_cookie_consent"),
    path("plaque-professionnelle/", views.plaque_by_url, name="plaque_by_url"),
    path("plaque-maison/", views.plaque_by_url, name="plaque_by_url"),
    path('get-products-by-subcategory/', views.get_products_by_subcategory, name='get_products_by_subcategory'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)