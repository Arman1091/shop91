# Generated by Django 5.1.4 on 2025-03-29 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_product_height_alter_product_width'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thickness',
            name='value',
            field=models.IntegerField(),
        ),
    ]
