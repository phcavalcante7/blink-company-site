from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Camiseta, Categoria, Pedido, ItemPedido, ImagemCamiseta

class ImagemInline(admin.TabularInline):
    model = ImagemCamiseta
    extra = 1

@admin.register(Camiseta)
class CamisetaAdmin(admin.ModelAdmin):
    exclude = ('modelo',)  # ← oculta o campo 'modelo' no admin

    list_display = ('nome', 'categoria', 'ordem', 'imagem_preview')
    inlines = [ImagemInline]
    prepopulated_fields = {"slug": ("nome",)}
    list_editable = ('ordem',)
    ordering = ('ordem',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'ajustar-estoque/<int:camiseta_id>/<str:modelo>/<str:tamanho>/<str:acao>/',
                self.admin_site.admin_view(self.ajustar_estoque),
                name='ajustar_estoque'
            ),
        ]
        return custom_urls + urls

    def ajustar_estoque(self, request, camiseta_id, modelo, tamanho, acao):
        camiseta = Camiseta.objects.get(id=camiseta_id)
        estoque = camiseta.estoque
        atual = estoque[modelo][tamanho]

        if acao == 'mais':
            estoque[modelo][tamanho] = atual + 1
        elif acao == 'menos':
            estoque[modelo][tamanho] = max(0, atual - 1)

        camiseta.estoque = estoque
        camiseta.save()

        messages.success(request, f'Estoque atualizado: {modelo.upper()} {tamanho} agora tem {estoque[modelo][tamanho]} unidades.')
        return redirect(f'/admin/camisetas/camiseta/{camiseta_id}/change/')

    def imagem_preview(self, obj):
        primeira_imagem = obj.imagens.first()
        if primeira_imagem:
            return format_html('<img src="{}" width="50" />', primeira_imagem.imagem.url)
        return "Sem imagem"
    imagem_preview.short_description = "Prévia"

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get('original')
        if obj:
            html = """
            <div style="margin: 1em 0; padding: 1em; background: #1a1a1a; border: 1px solid #333; border-radius: 6px">
            <h3 style="margin-top: 0; color: white;">Controle de Estoque</h3>
            """
            for modelo, tamanhos in obj.estoque.items():
                for tamanho, qtd in tamanhos.items():
                    url_mais = reverse('admin:ajustar_estoque', args=[obj.id, modelo, tamanho, 'mais'])
                    url_menos = reverse('admin:ajustar_estoque', args=[obj.id, modelo, tamanho, 'menos'])

                    html += (
                        f"<div style='margin-bottom:6px; font-family:monospace; color: white;'>"
                        f"<b>{modelo.upper()} {tamanho}</b>: {qtd} "
                        f"<a style='margin-left:6px;padding:2px 8px;background:#fff;color:#000;border-radius:4px;text-decoration:none;font-weight:bold' href='{url_mais}'>+</a>"
                        f"<a style='margin-left:4px;padding:2px 8px;background:#fff;color:#000;border-radius:4px;text-decoration:none;font-weight:bold' href='{url_menos}'>−</a>"
                        f"</div>"
                    )
            html += "</div>"
            context['adminform'].form.fields['descricao'].help_text = format_html(html)

        return super().render_change_form(request, context, *args, **kwargs)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('camiseta', 'modelo', 'tamanho', 'quantidade', 'preco_unitario', 'subtotal')

    def subtotal(self, obj):
        return f"R$ {obj.subtotal():.2f}"
    subtotal.short_description = "Subtotal"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'data', 'total', 'status']
    list_filter = ['status', 'data']
    search_fields = ['email']

    inlines = [ItemPedidoInline]

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'camiseta', 'modelo', 'tamanho', 'quantidade', 'preco_unitario')
    readonly_fields = ('pedido', 'camiseta', 'modelo', 'tamanho', 'quantidade', 'preco_unitario')
