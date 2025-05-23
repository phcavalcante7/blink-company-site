# Generated by Django 5.2 on 2025-04-17 21:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Camiseta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('preco_normal', models.DecimalField(decimal_places=2, max_digits=6)),
                ('preco_promo', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('modelo', models.CharField(choices=[('normal', 'Normal'), ('oversized', 'Oversized')], max_length=20)),
                ('genero', models.CharField(choices=[('masculino', 'Masculino'), ('feminino', 'Feminino')], max_length=10)),
                ('tamanhos_disponiveis', models.CharField(max_length=100)),
                ('imagem', models.ImageField(upload_to='camisetas/')),
                ('slug', models.SlugField(unique=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camisetas.categoria')),
            ],
        ),
    ]
