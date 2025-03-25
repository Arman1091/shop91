from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import (
    Customer, Category, SubCategory, Activity, Product, Material, PlaqueColor, TextColor, Police,
    CustomizedProduct, CustomizedLigneTexte, CustomizedStyleTexte, Wishlist, Cart, CartItem,
    Address, Payment, CookieConsent, ProductLigneTexte, LigneTexteStyle, ProductImage,
    ProductImageRelation, CustomizedProductLigneTexte, CustomizedLigneTexteStyle, LigneTexte, StyleTexte
)
from .forms import CustomerRegistrationForm, CustomerProfileForm, LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm
import re
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.core.mail import send_mail
from django.db.models import Q

stripe.api_key = settings.STRIPE_SECRET_KEY
DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

def get_cookie_consent(request):
    if request.user.is_authenticated:
        try:
            return request.user.cookie_consent.accepted
        except CookieConsent.DoesNotExist:
            return False
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
        'registration_form': registration_form,
        'login_form': login_form,
        'address_form': address_form
    }
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            cart_items = cart.items.all()
        except Cart.DoesNotExist:
            cart_items = []

        subtotal_ht = sum(item.get_subtotal() for item in cart_items)
        context['cart_items'] = cart_items
        context['subtotal_ht'] = subtotal_ht.quantize(Decimal('0.01'))
        context['total_ht'] = (subtotal_ht + context['shipping_ht']).quantize(Decimal('0.01'))
        context['tva'] = (context['total_ht'] * Decimal('0.20')).quantize(Decimal('0.01'))
        context['total_ttc'] = (context['total_ht'] + context['tva']).quantize(Decimal('0.01'))
    else:
        if 'pending_customizations' in request.session:
            pending_customizations = request.session['pending_customizations']
            cart_items = []
            for customization in pending_customizations:
                customized_product_id = customization.get('base_product_id')
                if customized_product_id:
                    customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id)
                    item = type('obj', (object,), {
                        'customized_product': customized_product,
                        'quantity': 1,
                        'get_subtotal': lambda self: calculate_subtotal(self.customized_product, self.quantity)
                    })()
                    cart_items.append(item)

            subtotal_ht = sum(item.get_subtotal() for item in cart_items)
            context['cart_items'] = cart_items
            context['subtotal_ht'] = round(subtotal_ht, 2)
            context['total_ht'] = round(subtotal_ht + context['shipping_ht'], 2)
            context['tva'] = 25  # 20% TVA
            context['total_ttc'] = round(context['total_ht'] + context['tva'], 2)

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
                subject = 'Confirmation de votre achat'
                message = f"""Bonjour {request.user.username},

Merci pour votre achat ! Voici les détails de votre commande :

- Montant total : {payment.amount} €
- Statut : {payment.status}
- ID de paiement : {payment.id}
- Articles achetés :
"""
                cart_items = payment.cart.items.all()
                for item in cart_items:
                    message += f"- {item.customized_product.base_product.name} (Quantité: {item.quantity}, Sous-total: {item.get_subtotal()} €)\n"

                message += """
Pour toute question, contactez-nous à admin@votre_site.com.

Cordialement,
L'équipe de Votre Site
"""
                send_mail(subject, message, DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
            else:
                payment.status = "failed"
                payment.save()
                messages.error(request, "Le paiement n’a pas été complété.")
        except stripe.error.StripeError as e:
            messages.error(request, f"Erreur lors de la vérification du paiement : {str(e)}")
        except Exception as e:
            messages.error(request, f"Erreur inattendue : {str(e)}")

    return render(request, "pages/success.html")

@csrf_exempt
def checkout_inscription(request):
    if request.method == "POST":
        try:
            form = CustomerRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@csrf_exempt
def checkout_connexion(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Mail ou mot de passe incorrect'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@csrf_exempt
def checkout_address(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    if customer.is_profile_complete:
        return redirect('home')
    
    if request.method == "POST":
        form = CustomerProfileForm(request.POST)
        try:
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
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Form is not valid'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return redirect('home')

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
                cart=cart,
                defaults={
                    "user": request.user,
                    "amount": total / 100,
                    "stripe_payment_id": f"pending_{cart.id}",
                    "status": "pending"
                }
            )

            if not created and payment.status in ["completed", "failed"]:
                messages.error(request, f"Ce panier a déjà été traité (statut: {payment.status}).")
                return redirect('view_cart')

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

@csrf_exempt
def checkout_livraison(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirige vers la connexion si l'utilisateur n'est pas authentifié

    try:
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        cart_items = cart.items.all()
        if not cart_items:
            messages.error(request, "Votre panier est vide.")
            return redirect('view_cart')

        # Calcul du total pour référence
        subtotal_ht = sum(item.get_subtotal() for item in cart_items)
        shipping_ht = Decimal('7.00')  # Exemple de frais de livraison fixes
        total_ht = subtotal_ht + shipping_ht
        tva = total_ht * Decimal('0.20')
        total_ttc = total_ht + tva

        if request.method == "POST":
            # Traitement des données de livraison (exemple : sélection d'une option de livraison)
            shipping_method = request.POST.get('shipping_method')
            if shipping_method:
                # Vous pouvez stocker cette information dans le panier ou une table dédiée
                cart.shipping_method = shipping_method  # Assurez-vous que ce champ existe dans le modèle Cart
                cart.save()
                return JsonResponse({'success': True, 'message': 'Méthode de livraison enregistrée'})
            else:
                return JsonResponse({'success': False, 'error': 'Veuillez sélectionner une méthode de livraison'})

        # Affichage du formulaire de livraison
        context = {
            'cart_items': cart_items,
            'subtotal_ht': subtotal_ht.quantize(Decimal('0.01')),
            'shipping_ht': shipping_ht.quantize(Decimal('0.01')),
            'total_ht': total_ht.quantize(Decimal('0.01')),
            'tva': tva.quantize(Decimal('0.01')),
            'total_ttc': total_ttc.quantize(Decimal('0.01')),
        }
        return render(request, 'pages/checkout_livraison.html', context)

    except Cart.DoesNotExist:
        messages.error(request, "Aucun panier actif trouvé.")
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f"Erreur lors du traitement de la livraison : {str(e)}")
        return redirect('checkout')
def test(request):

    return render(request, 'pages/test.html', {'message': 'Test réussi !'})
def test2(request):

    return render(request, 'pages/test.html', {'message': 'Test réussi !'})

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
        merge_session_with_user(self.request)
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

def all_categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.has_subcategories = category.subcategories.exists()
    return render(request, "pages/categories.html", {"categories": categories})


def editeur(request, category_slug,activity_slug, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        if product.activity.sub_category.category.slug_name != category_slug:
            raise Http404("Produit non trouvé dans cette catégorie.")
        
        image_relations = product.images.all()
        images = [relation.product_image for relation in image_relations]
        featured_image = product.images.filter(is_featured=True).first()
        lignes = ProductLigneTexte.objects.filter(product=product).select_related('ligne_texte', 'ligne_texte__police').prefetch_related('ligne_texte__styles__style')
        
        context = {
            'product': product,
            'images': images,
            'featured_image': featured_image.product_image if featured_image else None,
            'lignes': lignes,
            'materials': Material.objects.all(),
            'plaque_colors': PlaqueColor.objects.all(),
            'category_slug': category_slug,
        }
    else:
        category = get_object_or_404(Category, slug_name=category_slug)
        context = {
            'products': Product.objects.filter(activity__sub_category__category=category)[:5],
            'category_slug': category_slug,
        }

    return render(request, 'editeur/editeur.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    image_relations = product.images.all()
    images = [relation.product_image for relation in image_relations]
    featured_image = product.images.filter(is_featured=True).first()
    lignes = ProductLigneTexte.objects.filter(product=product)
    return render(request, 'editeur/editeur.html', {
        'product': product,
        'images': images,
        'featured_image': featured_image.product_image if featured_image else None,
        'lignes': lignes
    })



def customize_product(request, product_id):
    base_product = get_object_or_404(Product, id=product_id)
    materials = Material.objects.all()
    plaque_colors = PlaqueColor.objects.all()

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

        # Étape 1 : Sauvegarde du produit personnalisé
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
            customized_product.save()

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

                    ligne_texte = CustomizedLigneTexte.objects.create(
                        texte=texte,
                        police=Police.objects.filter(nom=style_dict["font-family"].group(1)).first() if style_dict["font-family"] else Police.objects.first(),
                        taille_police=tailles[i] if i < len(tailles) else (int(style_dict["font-size"].group(1)) if style_dict["font-size"] else 14),
                        position_x=int(style_dict["left"].group(1)) if style_dict["left"] else 0,
                        position_y=int(style_dict["top"].group(1)) if style_dict["top"] else i * 20,
                    )

                    CustomizedProductLigneTexte.objects.create(
                        customized_product=customized_product,
                        ligne_texte=ligne_texte
                    )

                    CustomizedLigneTexteStyle.objects.create(
                        ligne_texte=ligne_texte,
                        style=style
                    )

            # Étape 2 : Ajout au panier pour utilisateur authentifié
            cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, customized_product=customized_product)
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()

            # Réponse JSON
            response_data = {
                "success": True,
                "message": "Ajouté au panier avec succès !",
                "customized_product_id": customized_product.id,
                "product_name": base_product.name,
                "logo_url": customized_product.logo.url if customized_product.logo else None,
                "material_name": Material.objects.get(id=customization_data["material_id"]).name if customization_data["material_id"] else "N/A",
                "color_name": PlaqueColor.objects.get(id=customization_data["plaque_color_id"]).name if customization_data["plaque_color_id"] else "N/A",
            }
            return JsonResponse(response_data)

        else:
            # Gestion pour utilisateur non authentifié
            if "pending_customizations" not in request.session:
                request.session["pending_customizations"] = []
            customization_id = len(request.session["pending_customizations"])
            customization_data["temp_id"] = customization_id
            request.session["pending_customizations"].append(customization_data)

            # Ajout au panier dans la session
            if "cart" not in request.session:
                request.session["cart"] = {}
            cart = request.session["cart"]
            cart[str(customization_id)] = cart.get(str(customization_id), 0) + 1
            request.session["cart"] = cart
            request.session.modified = True

            # Réponse JSON
            response_data = {
                "success": True,
                "message": "Ajouté au panier avec succès (session) !",
                "customized_product_id": customization_id,
                "product_name": base_product.name,
                "logo_url": customization_data["logo"].name if customization_data["logo"] else None,
                "material_name": Material.objects.get(id=customization_data["material_id"]).name if customization_data["material_id"] else "N/A",
                "color_name": PlaqueColor.objects.get(id=customization_data["plaque_color_id"]).name if customization_data["plaque_color_id"] else "N/A",
            }
            return JsonResponse(response_data)

    # GET request : rendu du formulaire
    return render(request, "pages/customize_product.html", {
        "product": base_product,
        "materials": materials,
        "plaque_colors": plaque_colors,
    })

def customization_success(request, customized_product_id):
    if request.user.is_authenticated:
        customized_product = get_object_or_404(CustomizedProduct, id=customized_product_id)
    else:
        pending_customizations = request.session.get("pending_customizations", [])
        try:
            customized_product_id_int = int(customized_product_id)
            customized_product = next((item for item in pending_customizations if item.get("temp_id") == customized_product_id_int), None)
            if not customized_product and customized_product_id_int < len(pending_customizations):
                customized_product = pending_customizations[customized_product_id_int]
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


def customization_success_temp(request, temp_id=None):
    """
    Vue pour afficher une confirmation de personnalisation temporaire (non authentifié).
    """
    pending_customizations = request.session.get("pending_customizations", [])
    
    if temp_id is None:
        messages.error(request, "Aucun ID de personnalisation temporaire fourni.")
        return redirect('home')
    
    try:
        temp_id_int = int(temp_id)
        customized_product = next(
            (item for item in pending_customizations if item.get("temp_id") == temp_id_int), None
        )
        if not customized_product and temp_id_int < len(pending_customizations):
            customized_product = pending_customizations[temp_id_int]
        
        if not customized_product:
            messages.error(request, "Personnalisation temporaire introuvable.")
            return redirect('home')

        # Récupérer le produit de base associé
        base_product = get_object_or_404(Product, id=customized_product["base_product_id"])

        context = {
            "customized_product": customized_product,
            "base_product": base_product,
            "customized_product_id": temp_id,
            "is_authenticated": False,
        }
        return render(request, "pages/customization_success.html", context)
    
    except (ValueError, IndexError):
        messages.error(request, "ID de personnalisation temporaire invalide.")
        return redirect('home')

def add_to_wishlist(request, customized_product_id):
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

def view_wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, "pages/wishlist.html", {"wishlist_items": wishlist_items, "is_authenticated": True})
    else:
        wishlist = request.session.get("wishlist", [])
        wishlist_items = [{"customized_product": get_object_or_404(CustomizedProduct, id=product_id)} for product_id in wishlist]
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
            cart[str(customized_product_id)] = cart.get(str(customized_product_id), 0) + 1
            request.session["cart"] = cart
            return JsonResponse({"message": "Ajouté au panier (session) !"})
    except ValueError:
        return JsonResponse({"message": "ID invalide"}, status=400)

def view_cart(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
        except Cart.DoesNotExist:
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
                customized_product = next((item for item in pending_customizations if item.get("temp_id") == product_id_int), None)
                if not customized_product and product_id_int < len(pending_customizations):
                    customized_product = pending_customizations[product_id_int]
                if customized_product:
                    subtotal = calculate_subtotal_temp(customized_product, quantity)
                    cart_items.append({"customized_product": customized_product, "quantity": quantity, "subtotal": subtotal})
                    total += subtotal
            except (ValueError, IndexError):
                pass
        return render(request, "pages/carte.html", {"cart_items": cart_items, "total": total, "is_authenticated": False})

def calculate_subtotal_temp(customized_product, quantity):
    base_product = get_object_or_404(Product, id=customized_product["base_product_id"])
    base_price = base_product.activity.fixed_price
    material_id = customized_product.get("material_id")
    if material_id:
        material = Material.objects.get(id=material_id)
        material_price = MaterialThicknessPrice.objects.filter(material=material).first().price_per_square_meter
        area = (base_product.width * base_product.height) / 10000
        total_price = base_price + (material_price * area)
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
    
    cookie_consent = request.COOKIES.get('cookie_consent', 'declined') == 'accepted'
    if cookie_consent:
        CookieConsent.objects.update_or_create(user=request.user, defaults={"accepted": True})

    pending_customizations = request.session.get("pending_customizations", [])
    temp_id_to_product = {}
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

                ligne_texte = CustomizedLigneTexte.objects.create(
                    texte=texte,
                    police=Police.objects.filter(nom=style_dict["font-family"].group(1)).first() if style_dict["font-family"] else Police.objects.first(),
                    taille_police=tailles[i] if i < len(tailles) else (int(style_dict["font-size"].group(1)) if style_dict["font-size"] else 14),
                    position_x=int(style_dict["left"].group(1)) if style_dict["left"] else 0,
                    position_y=int(style_dict["top"].group(1)) if style_dict["top"] else i * 20,
                )

                CustomizedProductLigneTexte.objects.create(
                    customized_product=customized_product,
                    ligne_texte=ligne_texte
                )

                CustomizedLigneTexteStyle.objects.create(
                    ligne_texte=ligne_texte,
                    style=style
                )

    if "pending_customizations" in request.session:
        del request.session["pending_customizations"]

    session_wishlist = request.session.get("wishlist", [])
    for product_id in session_wishlist:
        try:
            product_id_int = int(product_id)
            customized_product = temp_id_to_product.get(product_id_int) or get_object_or_404(CustomizedProduct, id=product_id_int)
            if not customized_product.user:
                customized_product.user = request.user
                customized_product.save()
            Wishlist.objects.get_or_create(user=request.user, customized_product=customized_product)
        except ValueError:
            pass

    if "wishlist" in request.session:
        del request.session["wishlist"]

    session_cart = request.session.get("cart", {})
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    for product_id, quantity in session_cart.items():
        try:
            product_id_int = int(product_id)
            customized_product = temp_id_to_product.get(product_id_int) or get_object_or_404(CustomizedProduct, id=product_id_int)
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
            pass

    if "cart" in request.session:
        del request.session["cart"]

def set_cookie_consent(request):
    if request.method == "POST":
        consent = request.POST.get("consent") == "accept"
        if request.user.is_authenticated:
            CookieConsent.objects.update_or_create(user=request.user, defaults={"accepted": consent})
            return JsonResponse({"message": "Consentement enregistré en base"})
        else:
            response = JsonResponse({"message": "Consentement enregistré dans un cookie"})
            response.set_cookie("cookie_consent", "accepted" if consent else "declined", max_age=31536000)
            return response
    return JsonResponse({"message": "Requête invalide"}, status=400)

def cookie_policy(request):
    return render(request, "pages/cookie_policy.html")


def plaque_by_url(request):
    if request.method == 'GET':

        try:
            path = request.path  # Ex: "/plaque-professionnelle/"
            first_part = path.strip("/").split("/")[0]
            template_name = f"plaque/{first_part}.html"
            # Récupérer la catégorie "plaque-professionnelle" par son slug
            category = Category.objects.get(slug_name=first_part)
            
            # Récupérer toutes les sous-catégories de cette catégorie
            subcategories = SubCategory.objects.filter(category=category)
            
            # Vérifier si une sous-catégorie spécifique est demandée dans les paramètres GET
            subcategory_slug = request.GET.get('subcategory', None)
            
            if subcategory_slug:
                # Si un slug de sous-catégorie est fourni, essayer de la récupérer
                try:
                    selected_subcategory = SubCategory.objects.get(
                        slug_name=subcategory_slug,
                        category=category
                    )
                except SubCategory.DoesNotExist:
                    selected_subcategory = subcategories.first()  # Revenir à la première si invalide
            else:
                # Par défaut, prendre la première sous-catégorie
                selected_subcategory = subcategories.first() if subcategories.exists() else None
            
            # Récupérer les produits associés à la sous-catégorie sélectionnée
            if selected_subcategory:
                products = Product.objects.filter(activity__sub_category=selected_subcategory)
            else:
                products = Product.objects.none()  # Retourne un queryset vide si aucune sous-catégorie

            # Préparer le contexte pour le template
            context = {
                'category': category,
                'subcategories': subcategories,
                'selected_subcategory': selected_subcategory,
                'products': products,
            }
            
            return render(request, template_name, context)
        
        except Category.DoesNotExist:
            # Gérer le cas où la catégorie n'existe pas
            context = {
                'error': 'La catégorie  n\'existe pas.'
            }
            return render(request, template_name, context)
    
    # Si la méthode n'est pas GET, retourner une erreur ou rediriger selon vos besoins
    return render(request, template_name, {'error': 'Méthode non autorisée'})

# Nouvelle vue pour l'API AJAX
def get_products_by_subcategory(request):
    if request.method == 'GET':
        subcategory_slug = request.GET.get('subcategory')
        try:
            subcategory = SubCategory.objects.get(slug_name=subcategory_slug)
            products = Product.objects.filter(activity__sub_category=subcategory)
            
            # Préparer les données des produits avec category_slug et activity_slug
            products_data = []
            for product in products:
                featured_image = product.images.all().order_by('-is_featured').first()
                image_url = featured_image.product_image.image_url.url if featured_image else None
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'image_url': image_url or '/static/img/prof5.png',
                    'price': 18.00,  # À ajuster selon votre logique de prix
                    'category_slug': product.activity.sub_category.category.slug_name,  # Ex: "plaque-professionnelle"
                    'activity_slug': product.activity.slug_name,  # Ex: "medcine"
                })
            
            return JsonResponse({'products': products_data})
        except SubCategory.DoesNotExist:
            return JsonResponse({'error': 'Sous-catégorie non trouvée'}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def plaque_maison(request):

    return render(request, 'plaque/plaque-maison.html')