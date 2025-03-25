# Generated by Django 5.1.4 on 2025-03-22 07:13

import app.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('fixed_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('slug_name', models.SlugField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=app.models.activity_image_upload_path)),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=255)),
                ('complement_address', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug_name', models.SlugField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=app.models.category_image_upload_path)),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedLigneTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.CharField(max_length=100)),
                ('taille_police', models.PositiveIntegerField(default=14)),
                ('position_x', models.IntegerField(default=0)),
                ('position_y', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedStyleTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gras', models.BooleanField(default=False)),
                ('italique', models.BooleanField(default=False)),
                ('souligne', models.BooleanField(default=False)),
                ('couleur', models.CharField(default='#000000', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='materials/')),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlaqueColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF5733', 'Red'), ('#33FF57', 'Green')], default='#000000', max_length=100, unique=True)),
                ('hex_code', models.CharField(max_length=7, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Police',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.ImageField(upload_to=app.models.product_image_upload_path)),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StyleTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gras', models.BooleanField(default=False)),
                ('italique', models.BooleanField(default=False)),
                ('souligne', models.BooleanField(default=False)),
                ('couleur', models.CharField(default='#000000', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='TextColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF5733', 'Red'), ('#33FF57', 'Green')], default='#000000', max_length=100)),
                ('color', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Thickness',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('unit', models.CharField(default='mm', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CookieConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('consented_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cookie_consent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(blank=True, max_length=15, null=True)),
                ('is_profile_complete', models.BooleanField(default=False)),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.address')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('logo_width', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_position_x', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_position_y', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode', models.ImageField(blank=True, null=True, upload_to='qr_code/')),
                ('qrCode_width', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_position_x', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_position_y', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customized_products', to=settings.AUTH_USER_MODEL)),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.material')),
                ('plaque_color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.plaquecolor')),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedProductLigneTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customized_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='app.customizedproduct')),
                ('ligne_texte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customized_products', to='app.customizedlignetexte')),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedLigneTexteStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ligne_texte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='styles', to='app.customizedlignetexte')),
                ('style', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lignes', to='app.customizedstyletexte')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_payment_id', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='eur', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('completed', 'Complété'), ('failed', 'Échoué')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='app.cart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LigneTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.CharField(max_length=100)),
                ('taille_police', models.PositiveIntegerField(default=14)),
                ('position_x', models.IntegerField(default=0)),
                ('position_y', models.IntegerField(default=0)),
                ('police', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.police')),
            ],
        ),
        migrations.AddField(
            model_name='customizedlignetexte',
            name='police',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.police'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(null=True)),
                ('width', models.DecimalField(decimal_places=2, max_digits=5)),
                ('height', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_first_vu', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('logo_width', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_position_x', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('logo_position_y', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode', models.ImageField(blank=True, null=True, upload_to='qr_code/')),
                ('qrCode_width', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_position_x', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('qrCode_position_y', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.activity')),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.material')),
                ('plaque_color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.plaquecolor')),
                ('text_color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.textcolor')),
                ('thickness', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.thickness')),
            ],
        ),
        migrations.AddField(
            model_name='customizedproduct',
            name='base_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product'),
        ),
        migrations.CreateModel(
            name='ProductLigneTexte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ligne_texte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app.lignetexte')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='app.product')),
            ],
        ),
        migrations.CreateModel(
            name='LigneTexteStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ligne_texte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='styles', to='app.lignetexte')),
                ('style', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lignes', to='app.styletexte')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug_name', models.SlugField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=app.models.subcategory_image_upload_path)),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='app.category')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='app.subcategory'),
        ),
        migrations.AddField(
            model_name='customizedproduct',
            name='text_color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.textcolor'),
        ),
        migrations.AddField(
            model_name='customizedproduct',
            name='thickness',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.thickness'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.cart')),
                ('customized_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.customizedproduct')),
            ],
            options={
                'unique_together': {('cart', 'customized_product')},
            },
        ),
        migrations.CreateModel(
            name='ProductImageRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_featured', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.product')),
                ('product_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app.productimage')),
            ],
            options={
                'unique_together': {('product', 'product_image')},
            },
        ),
        migrations.CreateModel(
            name='MaterialThicknessPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_square_meter', models.DecimalField(decimal_places=2, max_digits=10)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='app.material')),
                ('thickness', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='app.thickness')),
            ],
            options={
                'unique_together': {('material', 'thickness')},
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('customized_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.customizedproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'customized_product')},
            },
        ),
    ]
