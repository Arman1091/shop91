import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings  # Ajout de l'importation




def product_image_upload_path(instance, filename):
    """
    Génère un chemin de stockage temporaire pour l'image.
    Format : products/uploads/YYYY/MM/DD/filename
    """
    date_path = timezone.now().strftime('%Y/%m/%d')
    filename = filename.lower().replace(" ", "_")
    return os.path.join("products", "uploads", date_path, filename)


 



def category_image_upload_path(instance, filename):
    """ Chemin : category/image/image_name """
    return os.path.join("category", "image", filename)

def subcategory_image_upload_path(instance, filename):
    """ Chemin : category/subcategory/image/image_name """
    return os.path.join(
        "category",
        instance.category.slug_name,
        "image",
        filename
    )

def activity_image_upload_path(instance, filename):
    """ Chemin : category/subcategory/activity/image/image_name """
    return os.path.join(
        "category",
        instance.sub_category.category.slug_name,
        instance.sub_category.slug_name,
        "activity",
        "image",
        filename
    )

class Address(models.Model):
    street_address = models.CharField(max_length=255)
    complement_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)    

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country} ({self.complement_address})"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Un Customer par User
    mobile = models.CharField(max_length=15, blank=True, null=True)  # Peut être vide au début
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)  
    is_profile_complete = models.BooleanField(default=False)  # Vérifier si l'adresse est complétée

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"



# Modèle Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug_name = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to=category_image_upload_path, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name


# Modèle SubCategory
class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    slug_name = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to=subcategory_image_upload_path, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name


# Modèle Activity
class Activity(models.Model):
    sub_category = models.ForeignKey(SubCategory, related_name='activities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    slug_name = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to=activity_image_upload_path, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name


# Modèle Material
class Material(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='materials/', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Modèle Thickness
class Thickness(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(max_length=10, default="mm")

    def __str__(self):
        return f"{self.value}{self.unit}"


# Modèle MaterialThicknessPrice
class MaterialThicknessPrice(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="prices")
    thickness = models.ForeignKey(Thickness, on_delete=models.CASCADE, related_name="prices")
    price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('material', 'thickness')

    def __str__(self):
        return f"{self.material.name} - {self.thickness.value}{self.thickness.unit}: {self.price_per_square_meter} €/m²"


# Modèle PlaqueColor
class PlaqueColor(models.Model):
    name = models.CharField(max_length=100, unique=True,choices=[('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF5733', 'Red'), ('#33FF57', 'Green')], default='#000000')
    hex_code = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return f"{self.name} ({self.hex_code})"


# Modèle TextColor
class TextColor(models.Model):
    name = models.CharField(max_length=100,choices=[('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF5733', 'Red'), ('#33FF57', 'Green')], default='#000000')
    color = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.name} ({self.color})"

class Police(models.Model):
    nom = models.CharField(max_length=100, unique=True)
   

    def __str__(self):
        return self.nom


# Modèle StyleTexte (inchangé)
class StyleTexte(models.Model):
    gras = models.BooleanField(default=False)
    italique = models.BooleanField(default=False)
    souligne = models.BooleanField(default=False)
    couleur = models.CharField(max_length=7, default="#000000")  # Code couleur hexadécimal
    
    def __str__(self):
        return f"Gras: {self.gras}, Italique: {self.italique}, Souligné: {self.souligne}, Couleur: {self.couleur}"

# Modèle Product (modifié pour supprimer la relation directe avec LigneTexte)
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    text_color = models.ForeignKey(TextColor, on_delete=models.SET_NULL, null=True, blank=True)
    plaque_color = models.ForeignKey(PlaqueColor, on_delete=models.SET_NULL, null=True, blank=True)
    thickness = models.ForeignKey(Thickness, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    is_first_vu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    logo_width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_position_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_position_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    qrCode = models.ImageField(upload_to='qr_code/', blank=True, null=True)
    qrCode_width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_position_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_position_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.name

# Modèle LigneTexte (modifié pour supprimer les relations directes)
class LigneTexte(models.Model):
    texte = models.CharField(max_length=100)  # Texte personnalisable par l'utilisateur
    police = models.ForeignKey(Police, on_delete=models.SET_NULL, null=True)
    taille_police = models.PositiveIntegerField(default=14)  # Taille de la police en points
    position_x = models.IntegerField(default=0)  # Position horizontale
    position_y = models.IntegerField(default=45)  # Position verticale
    
    def __str__(self):
        return f"Ligne {self.id} ({self.texte})"

# Modèle de pont entre Product et LigneTexte
class ProductLigneTexte(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="lignes")
    ligne_texte = models.ForeignKey(LigneTexte, on_delete=models.CASCADE, related_name="products")
    
    def __str__(self):
        return f"{self.product.name} - {self.ligne_texte.texte}"

# Modèle de pont entre LigneTexte et StyleTexte
class LigneTexteStyle(models.Model):
    ligne_texte = models.ForeignKey(LigneTexte, on_delete=models.CASCADE, related_name="styles")
    style = models.ForeignKey(StyleTexte, on_delete=models.SET_NULL, null=True, related_name="lignes")
    
    def __str__(self):
        return f"{self.ligne_texte.texte} - {self.style}"

# Modèle ProductImage (inchangé)
class ProductImage(models.Model):
    image_url = models.ImageField(upload_to=product_image_upload_path)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} ({self.image_url})"

class ProductImageRelation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    product_image = models.ForeignKey(ProductImage, on_delete=models.CASCADE, related_name="products")
    is_featured = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'product_image')

    def generate_custom_path(self, filename):
        category_name = self.product.activity.sub_category.category.slug_name
        subcategory_name = self.product.activity.sub_category.slug_name
        activity_name = self.product.activity.slug_name
        filename = filename.lower().replace(" ", "_")
        return os.path.join("products", category_name, subcategory_name, activity_name, filename)

    def save(self, *args, **kwargs):
        if self.pk is None:  # Si c'est une nouvelle relation
            old_path = self.product_image.image_url.path
            filename = os.path.basename(old_path)
            new_path = self.generate_custom_path(filename)
            full_new_path = os.path.join(settings.MEDIA_ROOT, new_path)
            
            # Créer le dossier si nécessaire et déplacer le fichier
            os.makedirs(os.path.dirname(full_new_path), exist_ok=True)
            if os.path.exists(old_path) and old_path != full_new_path:
                os.rename(old_path, full_new_path)
                self.product_image.image_url = new_path
                self.product_image.save()  # Met à jour l’URL dans ProductImage

        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.is_featured:
            existing_featured = ProductImageRelation.objects.filter(
                product=self.product, is_featured=True
            ).exclude(pk=self.pk)
            if existing_featured.exists():
                raise ValidationError("Ce produit a déjà une image en vedette.")

    def __str__(self):
        return f"{self.product.name} - Image {self.product_image.id} (Featured: {self.is_featured})"

        
# Modèle CustomizedStyleTexte (inchangé)
class CustomizedStyleTexte(models.Model):
    gras = models.BooleanField(default=False)
    italique = models.BooleanField(default=False)
    souligne = models.BooleanField(default=False)
    couleur = models.CharField(max_length=7, default="#000000")  # Code couleur hexadécimal
    
    def __str__(self):
        return f"Gras: {self.gras}, Italique: {self.italique}, Souligné: {self.souligne}, Couleur: {self.couleur}"

# Modèle CustomizedProduct (modifié pour supprimer la relation directe avec CustomizedLigneTexte)
class CustomizedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customized_products", null=True, blank=True)
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    text_color = models.ForeignKey(TextColor, on_delete=models.SET_NULL, null=True, blank=True)
    plaque_color = models.ForeignKey(PlaqueColor, on_delete=models.SET_NULL, null=True, blank=True)
    thickness = models.ForeignKey(Thickness, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    logo_width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_position_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    logo_position_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode = models.ImageField(upload_to='qr_code/', blank=True, null=True)
    qrCode_width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_position_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qrCode_position_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Personnalisation de {self.base_product.name} par {self.user.username if self.user else 'Utilisateur non connecté'}"

# Modèle CustomizedLigneTexte (modifié pour supprimer la relation directe)
class CustomizedLigneTexte(models.Model):
    texte = models.CharField(max_length=100)
    police = models.ForeignKey(Police, on_delete=models.SET_NULL, null=True)
    taille_police = models.PositiveIntegerField(default=14)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Ligne {self.id} ({self.texte})"

# Modèle de pont entre CustomizedProduct et CustomizedLigneTexte
class CustomizedProductLigneTexte(models.Model):
    customized_product = models.ForeignKey(CustomizedProduct, on_delete=models.CASCADE, related_name="lignes")
    ligne_texte = models.ForeignKey(CustomizedLigneTexte, on_delete=models.CASCADE, related_name="customized_products")
    
    def __str__(self):
        return f"{self.customized_product} - {self.ligne_texte.texte}"

# Modèle de pont entre CustomizedLigneTexte et CustomizedStyleTexte
class CustomizedLigneTexteStyle(models.Model):
    ligne_texte = models.ForeignKey(CustomizedLigneTexte, on_delete=models.CASCADE, related_name="styles")
    style = models.ForeignKey(CustomizedStyleTexte, on_delete=models.SET_NULL, null=True, related_name="lignes")
    
    def __str__(self):
        return f"{self.ligne_texte.texte} - {self.style}"


# Mise à jour de Wishlist et Cart pour utiliser CustomizedProduct
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    customized_product = models.ForeignKey(CustomizedProduct, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'customized_product')

    def __str__(self):
        return f"{self.user.username} - {self.customized_product}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Panier de {self.user.username} ({self.id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    customized_product = models.ForeignKey(CustomizedProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'customized_product')

    def get_subtotal(self):
        base_price = self.customized_product.base_product.activity.fixed_price
        if self.customized_product.material and self.customized_product.thickness:
            material_price = MaterialThicknessPrice.objects.get(
                material=self.customized_product.material, thickness=self.customized_product.thickness
            ).price_per_square_meter
            area = (self.customized_product.base_product.width * self.customized_product.base_product.height) / 10000
            total_price = base_price + (material_price * area)
        else:
            total_price = base_price
        return total_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.customized_product} dans panier {self.cart.id}"
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name="payment")
    stripe_payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="eur")
    status = models.CharField(max_length=20, default="pending", choices=[
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paiement {self.stripe_payment_id} - {self.user.username} - {self.amount} €"

class CookieConsent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cookie_consent", null=True, blank=True)
    accepted = models.BooleanField(default=False)
    consented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consentement de {self.user.username if self.user else 'Utilisateur anonyme'}: {'Accepté' if self.accepted else 'Refusé'}"