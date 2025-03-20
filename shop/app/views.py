from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Customer, Category, SubCategory, Activity, Product, Material, PlaqueColor, TextColor, Police, CustomizedProduct, CustomizedLigneTexte, CustomizedStyleTexte, Wishlist, Cart, CartItem,Address,Payment, CookieConsent
from .forms import CustomerRegistrationForm, CustomerProfileForm, LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm
import re
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

# Vues existantes
# views.py
def get_cookie_consent(request):
    if request.user.is_authenticated:
        try:
            return request.user.cookie_consent.accepted
        except CookieConsent.DoesNotExist:
            return False  # Par défaut, refusé si pas encore défini
    else:
        return request.COOKIES.get('cookie_consent', 'declined') == 'accepted'

def checkout(request):
    registration_form = CustomerRegistrationForm()
    login_form = LoginForm()
    address_form = CustomerProfileForm()
    context = {
    'cart_items': [],
    'subtotal_ht': Decimal('0.00'),
    'shipping_ht': Decimal('7.00'),
    'total_ht': Decimal('0.00'),
    'tva': Decimal('0.00'),
    'total_ttc': Decimal('0.00'),
    'registration_form':registration_form,
    'login_form':login_form,
    'address_form': address_form 
}
    
    if request.user.is_authenticated:
        # Fetch cart items from the database for authenticated users
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            cart_items = cart.items.all()  # Using related_name "items" from CartItem
        except Cart.DoesNotExist:
            cart_items = []

        # Calculate totals
        # ... calculate totals ...
        subtotal_ht = sum(item.get_subtotal() for item in cart_items)  # Already a Decimal
        context['subtotal_ht'] = subtotal_ht.quantize(Decimal('0.01'))
        context['total_ht'] = (subtotal_ht + context['shipping_ht']).quantize(Decimal('0.01'))
        context['tva'] = (context['total_ht'] * Decimal('0.20')).quantize(Decimal('0.01'))
        context['total_ttc'] = (context['total_ht'] + context['tva']).quantize(Decimal('0.01'))

    else:
        # Fetch cart items from session for guest users
        if 'pending_customizations' in request.session:
            pending_customizations = request.session['pending_customizations']
            cart_items = []
            for customization in pending_customizations:
                customized_product_id = customization.get('base_product_id')  # Assuming this key exists
                if customized_product_id:
                    customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id)
                    # Simulate a CartItem for guest calculation
                    item = type('obj', (object,), {
                        'customized_product': customized_product,
                        'quantity': 1,  # Default quantity for guest items
                        'get_subtotal': lambda self: self.customized_product.base_product.activity.fixed_price +
                                (self.customized_product.material.prices.get(thickness=customization.get('thickness')).price_per_square_meter *
                                 (customized_product.base_product.width * customized_product.base_product.height) / 10000) * self.quantity
                                 if customized_product.material and customization.get('thickness') else
                                 self.customized_product.base_product.activity.fixed_price * self.quantity
                    })()
                    cart_items.append(item)

            # Calculate totals
            subtotal_ht = sum(item.get_subtotal() for item in cart_items)
            context['cart_items'] = cart_items
            context['subtotal_ht'] = round(subtotal_ht, 2)
            context['total_ht'] = round(subtotal_ht + context['shipping_ht'], 2)
            context['tva'] = 25 # 20% TVA
            context['total_ttc'] = round(context['total_ht'] + context['tva'], 2)
        else:
            context['cart_items'] = []
        
    return render(request, 'pages/checkout.html', context)


def success(request):
    session_id = request.GET.get('session_id')
    payment_id = request.GET.get('payment_id')

    if session_id and payment_id:
        try:
            payment = get_object_or_404(Payment, id=payment_id, stripe_payment_id=session_id)
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment.status = "completed"
                payment.cart.is_active = False
                payment.cart.save()
                payment.save()
                messages.success(request, "Paiement effectué avec succès !")
                # Préparer l'e-mail
                subject = 'Confirmation de votre achat'
                message = f"""Bonjour {request.user.username},

Merci pour votre achat ! Voici les détails de votre commande :

- Montant total : {payment.amount} €
- Statut : {payment.status}
- ID de paiement : {payment.id}
- Articles achetés :
"""
                # Ajouter les détails des articles du panier
                cart_items = payment.cart.items.all()
                for item in cart_items:
                    message += f"- {item.customized_product.base_product.name} (Quantité: {item.quantity}, Sous-total: {item.get_subtotal()} €)\n"

                message += """
Pour toute question, contactez-nous à admin@votre_site.com.

Cordialement,
L'équipe de Votre Site
"""

                # Envoyer l'e-mail
                send_mail(
                    subject,
                    message,
                    DEFAULT_FROM_EMAIL,
                    [request.user.email],  # Envoyer à l'e-mail de l'utilisateur connecté
                    fail_silently=False,
                )
                print(f"E-mail envoyé à {request.user.email}")  # Débogage
            else:
                payment.status = "failed"
                payment.save()
                messages.error(request, "Le paiement n’a pas été complété.")
        except stripe.error.StripeError as e:
            messages.error(request, f"Erreur lors de la vérification du paiement : {str(e)}")
        except Exception as e:
            messages.error(request, f"Erreur inattendue : {str(e)}")

    return render(request, "success.html")


@csrf_exempt
def checkout_inscription(request):
    if request.method == "POST":
        
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        password = request.POST.get('password')
  
        print("xxx")
 
        if "new"== 'new':
            
            # Logic for new user registration (simplified)

            # Here you would typically create a new user
      

            form = CustomerRegistrationForm(request.POST)
            print(form)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:

                return JsonResponse({'success': False})

        else:
            # Logic for existing user login
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})

@csrf_exempt
def checkout_connexion(request):
    if request.method == "POST":
        
        email = request.POST.get('username')
        password = request.POST.get('password')
        form = LoginForm(data=request.POST)
        # response = super().form_valid(form)
        # merge_session_with_user(self.request)  # Appelé uniquement après connexion réussie
        # return response

        if form.is_valid():
            print("sd")
            user = authenticate(request, username=email, password=password)
    
            if user is not None:
                print("test1")
                login(request, user)
                return JsonResponse({'success': True})
            else:
                print("test1")
                return JsonResponse({'success': False,'error': 'mail ou mdp incorect'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})



@csrf_exempt
def checkout_address(request):
    print("sq")
    customer, created = Customer.objects.get_or_create(user=request.user)
    print("bbb")
    if customer.is_profile_complete:
        print("sqqs")
        return redirect('home')
    print ("sddsss")
    if request.method == "POST":
        form = CustomerProfileForm(request.POST)
        print("dsd")
        try:
            if form.is_valid():
                print("ssdddsss")
                customer.mobile = form.cleaned_data['mobile']
                address = Address(
                    street_address=form.cleaned_data['street_address'],
                    complement_address=form.cleaned_data['complement_address'],
                    city=form.cleaned_data['city'],
                    postal_code=form.cleaned_data['postal_code'],
                    country=form.cleaned_data['country'],
                )
                address.save()
                customer.address = address
                customer.is_profile_complete = True
                customer.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Form is not valid'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        initial_data = {
            'mobile': customer.mobile,
            'street_address': customer.address.street_address if customer.address else '',
            'complement_address': customer.address.complement_address if customer.address else '',
            'city': customer.address.city if customer.address else '',
            'postal_code': customer.address.postal_code if customer.address else '',
            'country': customer.address.country if customer.address else '',
        }
        form = CustomerProfileForm(initial=initial_data)

    # return render(request, "pages/complete_profile.html", {'form': form})
    print ("ssss")
    return redirect('home')

@csrf_exempt
def checkout_livraison(request):
    if request.method == "POST":
        delivery_method = request.POST.get('delivery_method')
        # Save delivery method logic here
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def checkout_payment(request):
    try:
        customer = request.user.customer
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        cart_items = cart.items.all()
        if not cart_items:
            messages.error(request, "Votre panier est vide.")
            return redirect('view_cart')

        total = sum(item.get_subtotal() for item in cart_items) * 100
        if total <= 0:
            messages.error(request, "Le montant total doit être supérieur à 0.")
            return redirect('view_cart')

        if request.method == "POST":
            payment, created = Payment.objects.get_or_create(
                cart=cart,  # Utilise le panier comme clé unique
                defaults={
                    "user": request.user,
                    "amount": total / 100,
                    "stripe_payment_id": f"pending_{cart.id}",
                    "status": "pending"
                }
            )

            if not created:
                if payment.status in ["completed", "failed"]:
                    messages.error(request, "Ce panier a déjà été traité (statut: %s)." % payment.status)
                    return redirect('view_cart')
                # Si le paiement est "pending", on peut recréer une session Stripe

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": "Achat Panier"},
                        "unit_amount": int(total),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"http://localhost:8000/success/?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment.id}",
                cancel_url="http://localhost:8000/cart/",
            )
            payment.stripe_payment_id = session.id
            payment.save()
            return redirect(session.url, code=303)

        return render(request, "pages/checkout.html", {"customer": customer, "cart": cart, "total": total / 100})

    except stripe.error.StripeError as e:
        messages.error(request, f"Erreur de paiement : {str(e)}")
        return redirect('view_cart')

def success(request):
    session_id = request.GET.get('session_id')
    payment_id = request.GET.get('payment_id')

    if session_id and payment_id:
        try:
            payment = get_object_or_404(Payment, id=payment_id, stripe_payment_id=session_id)
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment.status = "completed"
                payment.cart.is_active = False
                payment.cart.save()
                payment.save()
                messages.success(request, "Paiement effectué avec succès !")
            else:
                payment.status = "failed"
                payment.save()
                messages.error(request, "Le paiement n’a pas été complété.")
        except stripe.error.StripeError as e:
            messages.error(request, f"Erreur lors de la vérification du paiement : {str(e)}")
        except Exception as e:
            messages.error(request, f"Erreur inattendue : {str(e)}")

    return render(request, "pages/success.html")
@login_required
def complete_profile(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    if customer.is_profile_complete:
        return redirect('home')

    if request.method == "POST":
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            customer.mobile = form.cleaned_data['mobile']
            address = Address(
                street_address=form.cleaned_data['street_address'],
                complement_address=form.cleaned_data['complement_address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
            )
            address.save()
            customer.address = address
            customer.is_profile_complete = True
            customer.save()
            return redirect('home')
    else:
        initial_data = {
            'mobile': customer.mobile,
            'street_address': customer.address.street_address if customer.address else '',
            'complement_address': customer.address.complement_address if customer.address else '',
            'city': customer.address.city if customer.address else '',
            'postal_code': customer.address.postal_code if customer.address else '',
            'country': customer.address.country if customer.address else '',
        }
        form = CustomerProfileForm(initial=initial_data)

    return render(request, "pages/complete_profile.html", {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

class CustomLoginView(auth_views.LoginView):
    template_name = "registrations/login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        merge_session_with_user(self.request)  # Appelé uniquement après connexion réussie
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'registrations/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Register Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'registrations/customerregistration.html', {'form': form})

def home(request):
    category_plaque_prof = Category.objects.filter(slug_name="plaque-professionnelle").first()
    category_plaque_maison = Category.objects.filter(slug_name="plaque-pour-la-maison").first()
    plaque_prof_products = Product.objects.filter(activity__sub_category__category=category_plaque_prof, is_first_vu=True) if category_plaque_prof else Product.objects.none()
    plaque_maison_products = Product.objects.filter(activity__sub_category__category=category_plaque_maison, is_first_vu=True) if category_plaque_maison else Product.objects.none()
    return render(request, "pages/home.html", {'plaque_prof_products': plaque_prof_products, 'plaque_maison_products': plaque_maison_products})

def test(request):
    return render(request, "pages/test.html")

def test2(request):
    return render(request, "pages/test2.html")

def all_categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.has_subcategories = category.subcategories.exists()
    return render(request, "pages/categories.html", {"categories": categories})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'editeur/editeur.html', {'product': product})

def editeur(request, category_slug, product_id):
    category = get_object_or_404(Category, slug_name=category_slug)
    product = get_object_or_404(Product, id=product_id, activity__sub_category__category=category)
    materials = Material.objects.all()
    return render(request, 'editeur/editeur.html', {'product': product, 'all_categories': all_categories, "materials": materials})

def customize_product(request, product_id):
    base_product = get_object_or_404(Product, id=product_id)
    materials = Material.objects.all()
    plaque_colors = PlaqueColor.objects.all()
 
    
    # Vérifie le consentement
    # Vérifie le consentement
    # Vérifie le consentement sécurisé

    if request.method == "POST":
        customization_data = {
            "base_product_id": base_product.id,
            "material_id": request.POST.get("material"),
            "plaque_color_id": request.POST.get("plaque_color"),
            "logo": request.FILES.get("logo"),
            "logo_width": request.POST.get("logo_width"),
            "logo_height": request.POST.get("logo_height"),
            "logo_position_x": request.POST.get("logo_position_x"),
            "logo_position_y": request.POST.get("logo_position_y"),
            "qrCode": request.FILES.get("qrCode"),
            "qrCode_width": request.POST.get("qrCode_width"),
            "qrCode_height": request.POST.get("qrCode_height"),
            "qrCode_position_x": request.POST.get("qrCode_position_x"),
            "qrCode_position_y": request.POST.get("qrCode_position_y"),
            "textes": request.POST.getlist("texte[]"),
            "tailles": request.POST.getlist("taille_police[]"),
            "hidden_textes": request.POST.getlist("hidden_texte[]"),
        }

        if request.user.is_authenticated:
            customized_product = CustomizedProduct(
                user=request.user,
                base_product=base_product,
                material_id=customization_data["material_id"],
                plaque_color_id=customization_data["plaque_color_id"],
                logo=customization_data["logo"],
                logo_width=customization_data["logo_width"],
                logo_height=customization_data["logo_height"],
                logo_position_x=customization_data["logo_position_x"],
                logo_position_y=customization_data["logo_position_y"],
                qrCode=customization_data["qrCode"],
                qrCode_width=customization_data["qrCode_width"],
                qrCode_height=customization_data["qrCode_height"],
                qrCode_position_x=customization_data["qrCode_position_x"],
                qrCode_position_y=customization_data["qrCode_position_y"],
            )
            print("sqsssssssssssssssssss")
            customized_product.save()
            print("eeeee")

            textes = customization_data["textes"]
            tailles = customization_data["tailles"]
            hidden_textes = customization_data["hidden_textes"]
            print("ssssppppp")
            for i, texte in enumerate(textes):
                if texte:
                    hidden_style = hidden_textes[i] if i < len(hidden_textes) else ""
                    style_dict = {
                        "font-size": re.search(r"font-size:\s*(\d+)px", hidden_style),
                        "color": re.search(r"color:\s*(#[0-9a-fA-F]{6})", hidden_style),
                        "font-weight": re.search(r"font-weight:\s*bold", hidden_style),
                        "font-style": re.search(r"font-style:\s*italic", hidden_style),
                        "text-decoration": re.search(r"text-decoration:\s*underline", hidden_style),
                        "font-family": re.search(r"font-family:\s*([^;]+)", hidden_style),
                        "left": re.search(r"left:\s*(\d+)px", hidden_style),
                        "top": re.search(r"top:\s*(\d+)px", hidden_style),
                    }

                    style = CustomizedStyleTexte.objects.create(
                        gras=bool(style_dict["font-weight"]),
                        italique=bool(style_dict["font-style"]),
                        souligne=bool(style_dict["text-decoration"]),
                        couleur=style_dict["color"].group(1) if style_dict["color"] else "#000000",
                    )

                    CustomizedLigneTexte.objects.create(
                        customized_product=customized_product,
                        texte=texte,
                        police=Police.objects.filter(nom=style_dict["font-family"].group(1)).first() if style_dict["font-family"] else Police.objects.first(),
                        taille_police=tailles[i] if i < len(tailles) else (int(style_dict["font-size"].group(1)) if style_dict["font-size"] else 14),
                        position_x=int(style_dict["left"].group(1)) if style_dict["left"] else 0,
                        position_y=int(style_dict["top"].group(1)) if style_dict["top"] else i * 20,
                        style=style
                    )
                    print("llllllll")

            return redirect("customization_success", customized_product_id=customized_product.id)
        else:
            
            if "pending_customizations" not in request.session:
                request.session["pending_customizations"] = []
            customization_id = len(request.session["pending_customizations"])
            customization_data["temp_id"] = customization_id
            request.session["pending_customizations"].append(customization_data)
            request.session.modified = True
            return redirect("customization_success", customized_product_id=customization_id)
    print("test")

    return render(request, "pages/customize_product.html", {
        "product": base_product,
        "materials": materials,
        "plaque_colors": plaque_colors,
    })

# Nouvelle vue pour succès temporaire (non connecté)
def customization_success_temp(request):
    return render(request, "pages/customization_success_temp.html")

def customization_success(request, customized_product_id):
    if request.user.is_authenticated:
        customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id)
    else:
        pending_customizations = request.session.get("pending_customizations", [])
        # Recherche avec gestion des cas où "temp_id" peut manquer
        customized_product = None
        try:
            customized_product_id_int = int(customized_product_id)
            for item in pending_customizations:
                # Vérifie si "temp_id" existe, sinon utilise une logique alternative
                item_id = item.get("temp_id", None)
                if item_id is not None and item_id == customized_product_id_int:
                    customized_product = item
                    break
            if not customized_product:
                # Si rien n’est trouvé avec temp_id, on peut supposer un index basé sur l’ordre
                customized_product = pending_customizations[customized_product_id_int] if customized_product_id_int < len(pending_customizations) else None
        except (ValueError, IndexError):
            messages.error(request, "Personnalisation introuvable.")
            return redirect('home')

        if not customized_product:
            messages.error(request, "Personnalisation introuvable.")
            return redirect('home')

    return render(request, "pages/customization_success.html", {
        "customized_product": customized_product,
        "customized_product_id": customized_product_id,
        "is_authenticated": request.user.is_authenticated
    })

# Nouvelles vues pour panier, wishlist, sessions, et paiement
def add_to_wishlist(request, customized_product_id):
    # Vérifie le consentement sécurisé
    customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id)
    if request.user.is_authenticated:
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, customized_product=customized_product)
        if created:
            return JsonResponse({"message": "Ajouté à la wishlist !"})
        return JsonResponse({"message": "Déjà dans la wishlist."})
    else:
        if "wishlist" not in request.session:
            request.session["wishlist"] = []
        wishlist = request.session["wishlist"]
        if customized_product_id not in wishlist:
            wishlist.append(customized_product_id)
            request.session["wishlist"] = wishlist
            return JsonResponse({"message": "Ajouté à la wishlist (session) !"})
        return JsonResponse({"message": "Déjà dans la wishlist (session)."})

# views.py
def view_wishlist(request):
    cookie_consent = request.user.cookie_consent.accepted if request.user.is_authenticated else (request.COOKIES.get('cookie_consent', 'declined') == 'accepted')
    if not cookie_consent:
        return JsonResponse({"message": "Veuillez accepter les cookies pour ajouter au panier."}, status=403)
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, "pages/wishlist.html", {"wishlist_items": wishlist_items, "is_authenticated": True})
    else:
        wishlist = request.session.get("wishlist", [])
        wishlist_items = []
        for product_id in wishlist:
            customized_product = get_object_or_404(CustomizedProduct, id=product_id)
            wishlist_items.append({"customized_product": customized_product})
        return render(request, "pages/wishlist.html", {"wishlist_items": wishlist_items, "is_authenticated": False})

def add_to_cart(request, customized_product_id):
    try:
        customized_product_id_int = int(customized_product_id)
        if request.user.is_authenticated:
            customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id_int)
            cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, customized_product=customized_product)
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            return JsonResponse({"message": "Ajouté au panier !"})
        else:
            if "cart" not in request.session:
            
                request.session["cart"] = {}
            
            cart = request.session["cart"]
            
            if str(customized_product_id) in cart:
            
                cart[str(customized_product_id)] += 1
            
            else:
            
                cart[str(customized_product_id)] = 1
            
            request.session["cart"] = cart
            
            return JsonResponse({"message": "Ajouté au panier (session) !"})
           
    except ValueError:
        return JsonResponse({"message": "ID invalide"}, status=400)


def view_cart(request):
    # Vérifie le consentement sécurisé
    # cookie_consent = get_cookie_consent(request)
    # if not cookie_consent:
    #     messages.warning(request, "Veuillez accepter les cookies pour voir votre panier.")
    #     return redirect('home')

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
        except Cart.DoesNotExist:
            messages.info(request, "Aucun panier actif trouvé. Créez un nouveau panier.")
            cart = Cart.objects.create(user=request.user, is_active=True)
        cart_items = cart.items.all()
        total = sum(item.get_subtotal() for item in cart_items)
        return render(request, "pages/carte.html", {"cart_items": cart_items, "total": total, "is_authenticated": True})
    else:
        cart = request.session.get("cart", {})
        cart_items = []
        total = 0
        pending_customizations = request.session.get("pending_customizations", [])
        for product_id, quantity in cart.items():
            try:
                product_id_int = int(product_id)
                customized_product = None
                # Recherche avec "temp_id" ou index
                for item in pending_customizations:
                    item_id = item.get("temp_id", None)
                    if item_id is not None and item_id == product_id_int:
                        customized_product = item
                        break
                if not customized_product and product_id_int < len(pending_customizations):
                    customized_product = pending_customizations[product_id_int]

                if customized_product:
                    subtotal = calculate_subtotal_temp(customized_product, quantity)
                    cart_items.append({"customized_product": customized_product, "quantity": quantity, "subtotal": subtotal})
                    total += subtotal
            except (ValueError, IndexError):
                pass  # Ignore les entrées invalides
        return render(request, "pages/carte.html", {"cart_items": cart_items, "total": total, "is_authenticated": False})

    def plus_cart(request):
        if request.method == 'GET':
            prod_id = request.GET['prod_id']
            c= Cart.objects.get(Q(product = prod_id) & Q(user=request.user))
            print(c)
            c.quantity+=1
            c.save()
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity*p.product.discounted_price
                amount = amount+value
            totalamount = amount+40
            data={
                'quantity': c.quantity,
                'amount': amount,
                'totalamount':totalamount
            }
            return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c= Cart.objects.get(Q(product = prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity*p.product.discounted_price
            amount = amount+value
        totalamount = amount+40
        data={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def remove_cart(request):
    print("sd")
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c= Cart.objects.get(Q(product = prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity*p.product.discounted_price
            amount = amount+value
        totalamount = amount+40
        data={
            'amount': amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
# views.py
def calculate_subtotal_temp(customized_product, quantity):
    base_product = get_object_or_404(Product, id=customized_product["base_product_id"])
    base_price = base_product.activity.fixed_price
    material_id = customized_product.get("material_id")
    # Pas de "thickness" dans customization_data, on suppose que ce n’est pas utilisé ici
    if material_id:
        try:
            material = Material.objects.get(id=material_id)
            # Si tu veux inclure thickness, il faudrait ajouter "thickness_id" dans customization_data
            # Pour l’instant, on ignore thickness pour les utilisateurs non connectés
            material_price = MaterialThicknessPrice.objects.filter(material=material).first().price_per_square_meter
            area = (base_product.width * base_product.height) / 10000
            total_price = base_price + (material_price * area)
        except (Material.DoesNotExist, MaterialThicknessPrice.DoesNotExist):
            total_price = base_price
    else:
        total_price = base_price
    return total_price * quantity

def calculate_subtotal(customized_product, quantity):
    base_price = customized_product.base_product.activity.fixed_price
    if customized_product.material and customized_product.thickness:
        material_price = MaterialThicknessPrice.objects.get(
            material=customized_product.material, thickness=customized_product.thickness
        ).price_per_square_meter
        area = (customized_product.base_product.width * customized_product.base_product.height) / 10000
        total_price = base_price + (material_price * area)
    else:
        total_price = base_price
    return total_price * quantity

def merge_session_with_user(request):
    if not request.user.is_authenticated:
        return
    # Transférer le consentement cookie vers la base si connecté pour la première fois
    cookie_consent = request.COOKIES.get('cookie_consent', 'declined') == 'accepted'
    if cookie_consent:
        CookieConsent.objects.update_or_create(
            user=request.user,
            defaults={"accepted": True}
        )
    # Fusionner les personnalisations temporaires et créer les CustomizedProduct
    pending_customizations = request.session.get("pending_customizations", [])
    temp_id_to_product = {}  # Mappe temp_id à l’objet CustomizedProduct créé
    for customization_data in pending_customizations:
        customized_product = CustomizedProduct(
            user=request.user,
            base_product=get_object_or_404(Product, id=customization_data["base_product_id"]),
            material_id=customization_data["material_id"],
            plaque_color_id=customization_data["plaque_color_id"],
            logo=customization_data["logo"],
            logo_width=customization_data["logo_width"],
            logo_height=customization_data["logo_height"],
            logo_position_x=customization_data["logo_position_x"],
            logo_position_y=customization_data["logo_position_y"],
            qrCode=customization_data["qrCode"],
            qrCode_width=customization_data["qrCode_width"],
            qrCode_height=customization_data["qrCode_height"],
            qrCode_position_x=customization_data["qrCode_position_x"],
            qrCode_position_y=customization_data["qrCode_position_y"],
        )
        customized_product.save()

        # Associer temp_id à l’ID réel
        temp_id = customization_data.get("temp_id")
        if temp_id is not None:
            temp_id_to_product[temp_id] = customized_product

        textes = customization_data["textes"]
        tailles = customization_data["tailles"]
        hidden_textes = customization_data["hidden_textes"]

        for i, texte in enumerate(textes):
            if texte:
                hidden_style = hidden_textes[i] if i < len(hidden_textes) else ""
                style_dict = {
                    "font-size": re.search(r"font-size:\s*(\d+)px", hidden_style),
                    "color": re.search(r"color:\s*(#[0-9a-fA-F]{6})", hidden_style),
                    "font-weight": re.search(r"font-weight:\s*bold", hidden_style),
                    "font-style": re.search(r"font-style:\s*italic", hidden_style),
                    "text-decoration": re.search(r"text-decoration:\s*underline", hidden_style),
                    "font-family": re.search(r"font-family:\s*([^;]+)", hidden_style),
                    "left": re.search(r"left:\s*(\d+)px", hidden_style),
                    "top": re.search(r"top:\s*(\d+)px", hidden_style),
                }

                style = CustomizedStyleTexte.objects.create(
                    gras=bool(style_dict["font-weight"]),
                    italique=bool(style_dict["font-style"]),
                    souligne=bool(style_dict["text-decoration"]),
                    couleur=style_dict["color"].group(1) if style_dict["color"] else "#000000",
                )

                CustomizedLigneTexte.objects.create(
                    customized_product=customized_product,
                    texte=texte,
                    police=Police.objects.filter(nom=style_dict["font-family"].group(1)).first() if style_dict["font-family"] else Police.objects.first(),
                    taille_police=tailles[i] if i < len(tailles) else (int(style_dict["font-size"].group(1)) if style_dict["font-size"] else 14),
                    position_x=int(style_dict["left"].group(1)) if style_dict["left"] else 0,
                    position_y=int(style_dict["top"].group(1)) if style_dict["top"] else i * 20,
                    style=style
                )

    if "pending_customizations" in request.session:
        del request.session["pending_customizations"]

    # Fusionner la wishlist
    session_wishlist = request.session.get("wishlist", [])
    for product_id in session_wishlist:
        try:
            product_id_int = int(product_id)
            # Si c’est un temp_id, récupère le CustomizedProduct créé
            customized_product = temp_id_to_product.get(product_id_int)
            if customized_product:
                Wishlist.objects.get_or_create(user=request.user, customized_product=customized_product)
            else:
                # Si c’est un ID réel (cas rare), récupère-le
                customized_product = get_object_or_404(CustomizedProduct, id=product_id_int)
                if not customized_product.user:
                    customized_product.user = request.user
                    customized_product.save()
                Wishlist.objects.get_or_create(user=request.user, customized_product=customized_product)
        except ValueError:
            pass  # Ignore les ID invalides

    if "wishlist" in request.session:
        del request.session["wishlist"]

    # Fusionner le panier
    session_cart = request.session.get("cart", {})
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    for product_id, quantity in session_cart.items():
        try:
            product_id_int = int(product_id)
            # Si c’est un temp_id, récupère le CustomizedProduct créé
            customized_product = temp_id_to_product.get(product_id_int)
            if customized_product:
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, customized_product=customized_product)
                if not item_created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
            else:
                # Si c’est un ID réel (cas rare), récupère-le
                customized_product = get_object_or_404(CustomizedProduct, id=product_id_int)
                if not customized_product.user:
                    customized_product.user = request.user
                    customized_product.save()
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, customized_product=customized_product)
                if not item_created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
        except ValueError:
            pass  # Ignore les ID invalides

    if "cart" in request.session:
        del request.session["cart"]

# views.py
def set_cookie_consent(request):
    if request.method == "POST":
        consent = request.POST.get("consent") == "accept"
        if request.user.is_authenticated:
            CookieConsent.objects.update_or_create(
                user=request.user,
                defaults={"accepted": consent}
            )
            response = JsonResponse({"message": "Consentement enregistré en base"})
        else:
            response = JsonResponse({"message": "Consentement enregistré dans un cookie"})
            response.set_cookie(
                "cookie_consent",
                "accepted" if consent else "declined",
                max_age=31536000
            )
        return response
    return JsonResponse({"message": "Requête invalide"}, status=400)

def cookie_policy(request):
    return render(request, "pages/cookie_policy.html")



def plaque_professionnelle(request):

    return render(request, "plaque/plaque-professionnelle.html")

def plaque_maison(request):

    return render(request, "plaque/plaque-maison.html")