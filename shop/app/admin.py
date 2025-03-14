from django.contrib import admin
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin  
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
     Customer, Category, SubCategory, Activity, Material,
    Thickness, MaterialThicknessPrice, PlaqueColor, TextColor,
    Product, ProductImage,   Police, StyleTexte, LigneTexte, Address,
    CustomizedProduct, CustomizedStyleTexte, CustomizedLigneTexte,
    Wishlist, Cart, CartItem, Payment
)


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Enregistrement du modèle User avec CustomUserAdmin
admin.site.unregister(User)  # Désinscrire l'ancien UserAdmin
admin.site.register(User, CustomUserAdmin)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'postal_code', 'country')
    search_fields = ('street_address', 'city', 'postal_code', 'country')

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'is_profile_complete')  # Afficher les champs importants
    search_fields = ('user__email', 'mobile')  # Recherche par email et mobile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_name', 'image', 'image_preview', 'alt_text')
    list_editable = ('image', 'alt_text')
    fields = ('name', 'slug_name', 'image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Pas d'image"

    image_preview.short_description = "Aperçu"

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image', 'alt_text', 'image_preview')
    prepopulated_fields = {'slug_name': ('name',)}
    list_filter = ('category',)
    list_editable = ('image', 'alt_text')
    fields = ('name', 'slug_name', 'category', 'image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Pas d'image"

    image_preview.short_description = "Aperçu"

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category', 'fixed_price', 'image', 'alt_text', 'image_preview')
    prepopulated_fields = {'slug_name': ('name',)}
    list_filter = ('sub_category',)
    list_editable = ('image', 'alt_text')
    fields = ('name', 'slug_name', 'sub_category', 'image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Pas d'image"

    image_preview.short_description = "Aperçu"

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'alt_text')
    list_editable = ( 'description', 'alt_text')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "(Aucune image)"

    image_preview.short_description = "Aperçu"

    fields = ('name', 'description', 'image', 'alt_text')
    search_fields = ('name', 'description')
    list_filter = ('name',)

@admin.register(Thickness)
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ('value', 'unit')

@admin.register(MaterialThicknessPrice)
class MaterialThicknessPriceAdmin(admin.ModelAdmin):
    list_display = ('material', 'thickness', 'price_per_square_meter')
    list_filter = ('material', 'thickness')

@admin.register(PlaqueColor)
class PlaqueColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')

@admin.register(TextColor)
class TextColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Permet d'ajouter plusieurs images par défaut
    fields = ('image_url', 'alt_text', 'is_featured', 'image_preview')  # Ajout d’un aperçu d’image
    readonly_fields = ('image_preview',)  # Empêche la modification de l'aperçu

    def image_preview(self, obj):
        """Affiche un aperçu de l'image"""
        if obj.image_url:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image_url.url)
        return "Aucune image"

    image_preview.short_description = "Aperçu"

    def save_related(self, request, form, change):
        """Assure que les images sont correctement liées au produit après la sauvegarde"""
        super().save_related(request, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'alt_text', 'is_featured')  # Affiche les informations dans la liste
    list_filter = ('is_featured', 'product')  # Permet de filtrer par produit et par "is_featured"
    search_fields = ('product__name', 'alt_text')  # Recherche par nom de produit ou texte alternatif
    list_editable = ('alt_text', 'is_featured')  # Rendre ces champs modifiables directement dans la liste
    
    def image_preview(self, obj):
        """ Affiche un aperçu de l'image dans la liste """
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image_url.url)
        return "Pas d'image"

    image_preview.short_description = "Aperçu"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_image_preview', 'activity', 'text_color', 'plaque_color', 'thickness', 'material', 'width', 'height', 'is_first_vu', 'created_at', 'view_product_images', 'logo_width', 'logo_height', 'logo_position_x', 'logo_position_y','qrCode_width', 'qrCode_height', 'qrCode_position_x', 'qrCode_position_y')
    search_fields = ('name', 'activity__name', 'text_color__name', 'plaque_color__name')
    list_filter = ('is_first_vu', 'activity', 'text_color', 'plaque_color', 'thickness', 'material')
    list_editable = ('is_first_vu', 'text_color', 'plaque_color', 'thickness', 'material')
    inlines = [ProductImageInline]

    def main_image_preview(self, obj):
        featured_image = obj.images.filter(is_featured=True).first()
        if featured_image and featured_image.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', featured_image.image_url.url)
        return "Pas d'image"

    main_image_preview.short_description = "Image"

    def view_product_images(self, obj):
        url = reverse('admin:%s_%s_changelist' % (obj._meta.app_label, 'productimage'))
        return format_html('<a href="{}?product__id__exact={}">Voir les images</a>', url, obj.id)

    view_product_images.short_description = "Voir les images"

    



@admin.register(Police)
class PoliceAdmin(admin.ModelAdmin):
    list_display = ("nom", )
    search_fields = ("nom",)

@admin.register(StyleTexte)
class StyleTexteAdmin(admin.ModelAdmin):
    list_display = ("gras", "italique", "souligne", "couleur")
    list_filter = ("gras", "italique", "souligne")



@admin.register(LigneTexte)
class LigneTexteAdmin(admin.ModelAdmin):
    list_display = ("product", "texte", "police", "taille_police", "position_x", "position_y", "style")
    search_fields = ("texte",)
     
# Enregistrement de CustomizedProduct
@admin.register(CustomizedProduct)
class CustomizedProductAdmin(admin.ModelAdmin):
    list_display = ('base_product', 'user', 'material', 'plaque_color', 'created_at')
    list_filter = ('user', 'material', 'plaque_color', 'created_at')
    search_fields = ('base_product__name', 'user__username')

# Enregistrement de CustomizedStyleTexte
@admin.register(CustomizedStyleTexte)
class CustomizedStyleTexteAdmin(admin.ModelAdmin):
    list_display = ('gras', 'italique', 'souligne', 'couleur')
    list_filter = ('gras', 'italique', 'souligne')
    search_fields = ('couleur',)

# Enregistrement de CustomizedLigneTexte
@admin.register(CustomizedLigneTexte)
class CustomizedLigneTexteAdmin(admin.ModelAdmin):
    list_display = ('customized_product', 'texte', 'taille_police', 'position_x', 'position_y', 'police')
    list_filter = ('customized_product', 'police')
    search_fields = ('texte', 'customized_product__base_product__name')

# Enregistrement de Wishlist
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'customized_product', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'customized_product__base_product__name')

# Enregistrement de Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username',)

# Enregistrement de CartItem
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'customized_product', 'quantity', 'added_at', 'get_subtotal')
    list_filter = ('cart__is_active', 'added_at')
    search_fields = ('cart__user__username', 'customized_product__base_product__name')

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Sous-total'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'cart', 'stripe_payment_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'stripe_payment_id')