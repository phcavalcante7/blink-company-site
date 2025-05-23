# Generated by Django 5.2 on 2025-04-19 00:39

import camisetas.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camisetas', '0005_camiseta_descricao'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.AlterField(
            model_name='camiseta',
            name='estoque',
            field=models.JSONField(default=camisetas.models.estoque_padrao),
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modelo', models.CharField(max_length=20)),
                ('tamanho', models.CharField(max_length=10)),
                ('quantidade', models.PositiveIntegerField()),
                ('preco_unitario', models.DecimalField(decimal_places=2, max_digits=6)),
                ('camiseta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camisetas.camiseta')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='camisetas.pedido')),
            ],
        ),
    ]
