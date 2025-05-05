from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import JsonResponse
from .models import Camiseta

def enviar_email(pedido, destinatario):
    if not pedido or not destinatario:
        return

    contexto = {"pedido": pedido}

    # Renderiza HTML e versão texto
    html_content = render_to_string("emails/confirmacao.html", contexto)
    plain_text = strip_tags(html_content)

    assunto = f"Confirmação do Pedido #{pedido.id} · Blink"

    send_mail(
        subject=assunto,
        message=plain_text,  # fallback de texto
        from_email=settings.DEFAULT_FROM_EMAIL,  # ou use settings.DEFAULT_FROM_EMAIL
        recipient_list=[destinatario],
        html_message=html_content,
        fail_silently=False,
    )

def detalhes_modelo(request):
    camiseta_id = request.GET.get("camiseta_id")
    modelo = request.GET.get("modelo")

    try:
        camiseta = Camiseta.objects.get(id=camiseta_id)
        estoque = camiseta.estoque.get(modelo, {})
        medidas = {
            "normal": { "P": {"larg": 50, "comp": 71}, "M": {"larg": 51, "comp": 72}, "G": {"larg": 53, "comp": 75}, "GG": {"larg": 56, "comp": 77} },
            "oversized": { "P": {"larg": 53, "comp": 74}, "M": {"larg": 55, "comp": 77}, "G": {"larg": 57, "comp": 80}, "GG": {"larg": 61, "comp": 83} }
        }
        preco = 85 if modelo == "normal" else 95
        return JsonResponse({
            "estoque": estoque,
            "medidas": medidas.get(modelo, {}),
            "preco": preco
        })
    except Camiseta.DoesNotExist:
        return JsonResponse({"error": "Camiseta não encontrada"}, status=404)
