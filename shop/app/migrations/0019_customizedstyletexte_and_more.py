# Generated by Django 5.1.4 on 2025-03-02 14:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_product_qrcode_product_qrcode_height_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
        migrations.RemoveField(
            model_name='plaquecustomization',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='plaquecustomization',
            name='material',
        ),
        migrations.RemoveField(
            model_name='plaquecustomization',
            name='plaque_color',
        ),
        migrations.RemoveField(
            model_name='plaquecustomization',
            name='product',
        ),
        migrations.RemoveField(
            model_name='plaquecustomization',
            name='thickness',
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
                ('base_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product')),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.material')),
                ('plaque_color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.plaquecolor')),
                ('text_color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.textcolor')),
                ('thickness', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.thickness')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customized_products', to=settings.AUTH_USER_MODEL)),
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
                ('police', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.police')),
                ('style', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.styletexte')),
                ('customized_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='app.customizedproduct')),
            ],
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
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='PlaqueCustomization',
        ),
    ]
