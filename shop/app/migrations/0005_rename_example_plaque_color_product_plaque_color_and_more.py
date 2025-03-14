# Generated by Django 5.1.4 on 2025-02-19 22:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_product_is_first_vu'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='example_plaque_color',
            new_name='plaque_color',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='example_text_color',
            new_name='text_color',
        ),
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.material'),
        ),
        migrations.AddField(
            model_name='product',
            name='thickness',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.thickness'),
        ),
    ]
