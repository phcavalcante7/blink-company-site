from django.urls import path
from .views import (
    home,
    lista_camisetas,
    produto,
    adicionar_ao_carrinho,
    remover_do_carrinho,
    incrementar_item,
    decrementar_item,
    ver_carrinho,
    checkout,
    sucesso,
    webhook_stripe,
    meus_pedidos,
)
from .utils import enviar_email


urlpatterns = [
    path('', home, name='home'),
    path('camisetas/', lista_camisetas, name='lista_camisetas'),
    path('camisetas/<slug:slug>/', produto, name='produto'),
    path('adicionar-ao-carrinho/', adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', ver_carrinho, name='ver_carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('sucesso/', sucesso, name='sucesso'),
    path('remover-do-carrinho/<int:camiseta_id>/<str:modelo>/<str:tamanho>/', remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/incrementar/<int:camiseta_id>/<str:modelo>/<str:tamanho>/', incrementar_item, name='incrementar_item'),
    path('carrinho/decrementar/<int:camiseta_id>/<str:modelo>/<str:tamanho>/', decrementar_item, name='decrementar_item'),
    path('webhook/stripe/', webhook_stripe, name='webhook_stripe'),
    path("enviar-email/", enviar_email, name='enviar_email'),
    path("meus-pedidos/", meus_pedidos, name="meus_pedidos"),
]
