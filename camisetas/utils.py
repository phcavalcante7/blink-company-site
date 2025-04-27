from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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
