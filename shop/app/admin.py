from django.contrib import admin
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django import forms
from .models import (
    Customer, Category, SubCategory, Activity, Material, Thickness, MaterialThicknessPrice,
    PlaqueColor, TextColor, Product, ProductImage, ProductImageRelation, Police, StyleTexte,
    LigneTexte, ProductLigneTexte, LigneTexteStyle, Address, CustomizedProduct,
    CustomizedStyleTexte, CustomizedLigneTexte, CustomizedProductLigneTexte,
    CustomizedLigneTexteStyle, Wishlist, Cart, CartItem, Payment
)

# Admin personnalisé pour User
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Admin pour Address
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'postal_code', 'country')
    search_fields = ('street_address', 'city', 'postal_code', 'country')

# Admin pour Customer
@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'is_profile_complete')
    search_fields = ('user__email', 'mobile')

# Admin pour Category
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

# Admin pour SubCategory
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

# Admin pour Activity
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category', 'fixed_price', 'image', 'alt_text', 'image_preview')
    prepopulated_fields = {'slug_name': ('name',)}
    list_filter = ('sub_category',)
    list_editable = ('image', 'alt_text')
    fields = ('name', 'slug_name', 'sub_category', 'fixed_price', 'image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Pas d'image"
    
    image_preview.short_description = "Aperçu"

# Admin pour Material
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'alt_text')
    list_editable = ('description', 'alt_text')
    fields = ('name', 'description', 'image', 'alt_text')
    search_fields = ('name', 'description')
    list_filter = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "(Aucune image)"
    
    image_preview.short_description = "Aperçu"

# Admin pour Thickness
@admin.register(Thickness)
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ('value', 'unit')

# Admin pour MaterialThicknessPrice
@admin.register(MaterialThicknessPrice)
class MaterialThicknessPriceAdmin(admin.ModelAdmin):
    list_display = ('material', 'thickness', 'price_per_square_meter')
    list_filter = ('material', 'thickness')

# Admin pour PlaqueColor
@admin.register(PlaqueColor)
class PlaqueColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')

# Admin pour TextColor
@admin.register(TextColor)
class TextColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')

# Admin pour ProductImage
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'alt_text', 'created_at')
    search_fields = ('alt_text',)
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image_url.url)
        return "Pas d'image"
    
    image_preview.short_description = "Aperçu"

# Admin pour ProductImageRelation
@admin.register(ProductImageRelation)
class ProductImageRelationAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_image', 'is_featured', 'image_preview')
    list_filter = ('is_featured', 'product')
    search_fields = ('product__name', 'product_image__alt_text')
    list_editable = ('is_featured',)
    
    def image_preview(self, obj):
        if obj.product_image.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.product_image.image_url.url)
        return "Pas d'image"
    
    image_preview.short_description = "Aperçu"

# Inline pour ProductImageRelation
class ProductImageRelationForm(forms.ModelForm):
    new_image = forms.ImageField(label="Nouvelle image", required=True)

    class Meta:
        model = ProductImageRelation
        fields = ('product_image', 'is_featured')
        widgets = {'product_image': forms.Select(attrs={'required': False})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_image'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_image = self.cleaned_data.get('new_image')
        if new_image:
            product_image = ProductImage.objects.create(
                image_url=new_image,
                alt_text=self.instance.product.name if self.instance.product else "Image"
            )
            instance.product_image = product_image
        if commit:
            instance.save()
        return instance

class ProductImageRelationInline(admin.TabularInline):
    model = ProductImageRelation
    extra = 1
    form = ProductImageRelationForm
    fields = ('new_image', 'product_image', 'is_featured', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.product_image and obj.product_image.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.product_image.image_url.url)
        return "Pas d'image"
    
    image_preview.short_description = "Aperçu"

# Inline pour LigneTexteStyle
class LigneTexteStyleInline(admin.TabularInline):
    model = LigneTexteStyle
    extra = 1
    fields = ('style',)

# Custom form for ProductLigneTexte
class ProductLigneTexteForm(forms.ModelForm):
    texte = forms.CharField(max_length=255, required=False)
    police = forms.ModelChoiceField(queryset=Police.objects.all(), required=False)
    taille_police = forms.IntegerField(required=False)
    position_x = forms.IntegerField(required=False)
    position_y = forms.IntegerField(required=False)
    styles = forms.ModelMultipleChoiceField(
        queryset=StyleTexte.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '5'}),
        label="Styles existants"
    )
    new_styles = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter new styles (e.g., "gras=True, italique=False, couleur=#000000" per line)'}),
        label="Nouveaux styles"
    )

    class Meta:
        model = ProductLigneTexte
        fields = ('ligne_texte',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'ligne_texte') and self.instance.ligne_texte:
            self.fields['texte'].initial = self.instance.ligne_texte.texte
            self.fields['police'].initial = self.instance.ligne_texte.police
            self.fields['taille_police'].initial = self.instance.ligne_texte.taille_police
            self.fields['position_x'].initial = self.instance.ligne_texte.position_x
            self.fields['position_y'].initial = self.instance.ligne_texte.position_y
            try:
                self.fields['styles'].initial = [style.style.id for style in self.instance.ligne_texte.lignetextestyle_set.all()]
            except AttributeError:
                self.fields['styles'].initial = []

    def clean_new_styles(self):
        new_styles = self.cleaned_data['new_styles']
        if not new_styles:
            return []
        styles_list = []
        for line in new_styles.split('\n'):
            if line.strip():
                style_dict = {}
                for param in line.split(','):
                    try:
                        key, value = param.split('=')
                        key = key.strip()
                        value = value.strip()
                        if key in ['gras', 'italique', 'souligne']:
                            style_dict[key] = value.lower() == 'true'
                        elif key == 'couleur':
                            style_dict['couleur'] = value
                    except ValueError:
                        raise forms.ValidationError(f"Invalid style format in line: {line}")
                styles_list.append(style_dict)
        return styles_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        ligne_texte_data = {
            'texte': self.cleaned_data['texte'],
            'police': self.cleaned_data['police'],
            'taille_police': self.cleaned_data['taille_police'],
            'position_x': self.cleaned_data['position_x'],
            'position_y': self.cleaned_data['position_y'],
        }
        existing_styles = self.cleaned_data['styles']
        new_styles = self.cleaned_data['new_styles']

        if any(ligne_texte_data.values()):
            if hasattr(instance, 'ligne_texte') and instance.ligne_texte:
                for attr, value in ligne_texte_data.items():
                    setattr(instance.ligne_texte, attr, value)
                instance.ligne_texte.save()
            else:
                instance.ligne_texte = LigneTexte.objects.create(**ligne_texte_data)

            if instance.ligne_texte:
                LigneTexteStyle.objects.filter(ligne_texte=instance.ligne_texte).delete()
                for style in existing_styles:
                    LigneTexteStyle.objects.create(ligne_texte=instance.ligne_texte, style=style)
                for style_dict in new_styles:
                    style = StyleTexte.objects.create(**style_dict)
                    LigneTexteStyle.objects.create(ligne_texte=instance.ligne_texte, style=style)
        else:
            instance.ligne_texte = None

        if commit:
            instance.save()
        return instance

# Inline pour ProductLigneTexte
class ProductLigneTexteInline(admin.TabularInline):
    model = ProductLigneTexte
    extra = 1
    form = ProductLigneTexteForm
    fields = ('texte', 'police', 'taille_police', 'position_x', 'position_y', 'styles', 'new_styles', 'add_new_style_button')
    readonly_fields = ('add_new_style_button',)

    def add_new_style_button(self, obj):
        url = reverse('admin:%s_%s_add' % (StyleTexte._meta.app_label, StyleTexte._meta.model_name))
        return format_html(
            '<a class="btn" href="{}" target="_blank" onclick="window.open(this.href, \'_blank\', \'width=800,height=600\'); return false;">New</a>',
            url
        )
    add_new_style_button.short_description = "Ajouter un nouveau style"

# Admin pour Product avec les inlines
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_image_preview', 'activity', 'text_color', 'plaque_color', 'thickness', 'material', 'width', 'height', 'is_first_vu', "product_price", 'created_at', 'view_product_images')
    search_fields = ('name', 'activity__name', 'text_color__name', 'plaque_color__name')
    list_filter = ('is_first_vu', 'activity', 'text_color', 'plaque_color', 'thickness', 'material', 'product_price')
    list_editable = ('is_first_vu', 'text_color', 'plaque_color', 'thickness', 'material')
    inlines = [ProductImageRelationInline, ProductLigneTexteInline]

    def main_image_preview(self, obj):
        featured_relation = obj.images.filter(is_featured=True).first()
        if featured_relation and featured_relation.product_image.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', featured_relation.product_image.image_url.url)
        return "Pas d'image"

    main_image_preview.short_description = "Image"

    def view_product_images(self, obj):
        url = reverse('admin:%s_%s_changelist' % (obj._meta.app_label, 'productimagerelation'))
        return format_html('<a href="{}?product__id__exact={}">Voir les images</a>', url, obj.id)

    view_product_images.short_description = "Voir les images"

# Admin pour Police
@admin.register(Police)
class PoliceAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)

# Admin pour StyleTexte
@admin.register(StyleTexte)
class StyleTexteAdmin(admin.ModelAdmin):
    list_display = ("gras", "italique", "souligne", "couleur")
    list_filter = ("gras", "italique", "souligne")

# Admin pour LigneTexte
@admin.register(LigneTexte)
class LigneTexteAdmin(admin.ModelAdmin):
    list_display = ("texte", "police", "taille_police", "position_x", "position_y")
    search_fields = ("texte",)

# Admin pour ProductLigneTexte
@admin.register(ProductLigneTexte)
class ProductLigneTexteAdmin(admin.ModelAdmin):
    list_display = ('product', 'ligne_texte')
    search_fields = ('product__name', 'ligne_texte__texte')

# Admin pour LigneTexteStyle
@admin.register(LigneTexteStyle)
class LigneTexteStyleAdmin(admin.ModelAdmin):
    list_display = ('ligne_texte', 'style')
    search_fields = ('ligne_texte__texte',)

# Inline pour CustomizedProductLigneTexte
class CustomizedProductLigneTexteInline(admin.TabularInline):
    model = CustomizedProductLigneTexte
    extra = 1
    fields = ('ligne_texte',)
    readonly_fields = ('ligne_texte',)

# Admin pour CustomizedProduct avec gestion des PDF et JPEG
@admin.register(CustomizedProduct)
class CustomizedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_product', 'user', 'material', 'plaque_color', 'pdf_link', 'jpeg_link', 'created_at')
    list_filter = ('user', 'base_product', 'material', 'plaque_color', 'created_at')  # Temporarily remove problematic filters
    search_fields = ('base_product__name', 'user__username')
    inlines = [CustomizedProductLigneTexteInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'base_product', 'material', 'plaque_color')
        }),
        ('Logo Settings', {
            'fields': ('logo', 'logo_width', 'logo_height', 'logo_position_x', 'logo_position_y'),
        }),
        ('QR Code Settings', {
            'fields': ('qrCode', 'qrCode_width', 'qrCode_height', 'qrCode_position_x', 'qrCode_position_y'),
        }),
        ('Output Files', {
            'fields': ('pdf_field', 'jpeg_field'),
        }),
    )

    def pdf_link(self, obj):
        if hasattr(obj, 'pdf_field') and obj.pdf_field:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_field.url)
        return "No PDF"
    pdf_link.short_description = 'PDF'

    def jpeg_link(self, obj):
        if hasattr(obj, 'jpeg_field') and obj.jpeg_field:
            return format_html('<a href="{}" target="_blank">View JPEG</a>', obj.jpeg_field.url)
        return "No JPEG"
    jpeg_link.short_description = 'JPEG'

# Admin pour CustomizedStyleTexte
@admin.register(CustomizedStyleTexte)
class CustomizedStyleTexteAdmin(admin.ModelAdmin):
    list_display = ('gras', 'italique', 'souligne', 'couleur')
    list_filter = ('gras', 'italique', 'souligne')
    search_fields = ('couleur',)

# Admin pour CustomizedLigneTexte
@admin.register(CustomizedLigneTexte)
class CustomizedLigneTexteAdmin(admin.ModelAdmin):
    list_display = ("texte", "police", "taille_police", "position_x", "position_y")
    search_fields = ("texte",)

# Admin pour CustomizedProductLigneTexte
@admin.register(CustomizedProductLigneTexte)
class CustomizedProductLigneTexteAdmin(admin.ModelAdmin):
    list_display = ('customized_product', 'ligne_texte')
    search_fields = ('customized_product__base_product__name', 'ligne_texte__texte')

# Admin pour CustomizedLigneTexteStyle
@admin.register(CustomizedLigneTexteStyle)
class CustomizedLigneTexteStyleAdmin(admin.ModelAdmin):
    list_display = ('ligne_texte', 'style')
    search_fields = ('ligne_texte__texte',)

# Admin pour Wishlist
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'customized_product', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'customized_product__base_product__name')

# Admin pour Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username',)

# Admin pour CartItem
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'customized_product', 'quantity', 'added_at', 'get_subtotal')
    list_filter = ('cart__is_active', 'added_at')
    search_fields = ('cart__user__username', 'customized_product__base_product__name')

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Sous-total'

# Admin pour Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'cart', 'stripe_payment_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'stripe_payment_id')