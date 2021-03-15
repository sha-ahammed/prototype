# Generated by Django 3.1.7 on 2021-03-06 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20210306_1739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartmodel',
            name='product_name',
        ),
        migrations.CreateModel(
            name='cart_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='home.cartmodel')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='home.product')),
            ],
        ),
    ]
