import os
from django.db import models
from django.contrib.auth.models import User


def product_image_upload_path(instance, filename):
    """
    Génère le chemin de stockage pour l'image d'un produit sous la forme :
    products/category_name/subcategory_name/activity_name/filename
    """
    category_name = instance.product.activity.sub_category.category.slug_name
    subcategory_name = instance.product.activity.sub_category.slug_name
    activity_name = instance.product.activity.slug_name
    filename = filename.lower().replace(" ", "_")

    return os.path.join("products", category_name, subcategory_name, activity_name, filename)


# Modèle Address
class Address(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"

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

# Modèle Customer
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


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
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2)
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
    fichier = models.FileField(upload_to="polices/")  # Optionnel si tu veux gérer des fichiers de police

    def __str__(self):
        return self.nom
class StyleTexte(models.Model):
    gras = models.BooleanField(default=False)
    italique = models.BooleanField(default=False)
    souligne = models.BooleanField(default=False)
    couleur = models.CharField(max_length=7, default="#000000")  # Code couleur hexadécimal
    
    def __str__(self):
        return f"Gras: {self.gras}, Italique: {self.italique}, Souligné: {self.souligné}, Couleur: {self.couleur}"




# Modèle Product
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
    is_first_vu= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

     # Champs pour l'exemple de personnalisation de la plaque
    
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)  # Logo du produit pour l'exemple
    logo_width = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True)  # Largeur du logo en pixels
    logo_height = models.DecimalField(max_digits=5, decimal_places=2 ,null=True, blank=True)  # Hauteur du logo en pixels
    logo_position_x = models.DecimalField(max_digits=5, decimal_places=2 , null=True, blank=True) # Position X (décalage horizontal)
    logo_position_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Position Y (décalage vertical)
    def __str__(self):
        return self.name

class LigneTexte(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="lignes")
    texte = models.TextField(blank=True)  # Texte personnalisable par l'utilisateur
    police = models.ForeignKey(Police, on_delete=models.SET_NULL, null=True)
    taille_police = models.PositiveIntegerField(default=14)  # Taille de la police en points
    position_x = models.IntegerField(default=0)  # Position horizontale en pixels ou mm
    position_y = models.IntegerField(default=0)  # Position verticale en pixels ou mm
    style = models.ForeignKey(StyleTexte, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Ligne {self.id} ({self.texte}) sur {self.product.nom}"

# Modèle ProductImage
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.ImageField(upload_to=product_image_upload_path)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """ Empêche d'avoir plus d'une image en 'is_featured' par produit """
        if self.is_featured:
            existing_featured = ProductImage.objects.filter(product=self.product, is_featured=True).exclude(pk=self.pk)
            if existing_featured.exists():
                raise ValidationError("Ce produit a déjà une image en vedette.")

    def save(self, *args, **kwargs):
        self.clean()  # Appelle la validation avant d’enregistrer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


# Modèle PlaqueCustomization
class PlaqueCustomization(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    thickness = models.ForeignKey(Thickness, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    plaque_color = models.ForeignKey(PlaqueColor, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    text_line_1 = models.CharField(max_length=255, blank=True, null=True)
    text_line_2 = models.CharField(max_length=255, blank=True, null=True)
    text_line_3 = models.CharField(max_length=255, blank=True, null=True)
    text_line_4 = models.CharField(max_length=255, blank=True, null=True)
    text_line_5 = models.CharField(max_length=255, blank=True, null=True)
    text_line_6 = models.CharField(max_length=255, blank=True, null=True)

    def get_price(self):
        price = MaterialThicknessPrice.objects.filter(material=self.material, thickness=self.thickness).first()
        return (price.price_per_square_meter * self.width * self.height + self.product.activity.fixed_price) if price else 0.00

    def __str__(self):
        return f"Customization for {self.product.name} by {self.customer.user.username}"


# Modèle Order
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('shipped', 'Shipped')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.customer.user.username}"
