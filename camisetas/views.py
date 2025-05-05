from django.shortcuts import redirect, get_object_or_404, render
from .models import Camiseta, Pedido, ItemPedido
from django.contrib import messages
import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from camisetas.utils import enviar_email

# ---------Settings-----------
# ----------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
# ----------------------------

def adicionar_ao_carrinho(request):
    if request.method == 'POST':
        camiseta_id = request.POST.get('camiseta_id')
        modelo = request.POST.get('modelo')
        tamanho = request.POST.get('tamanho')

        if not tamanho:
            messages.error(request, "Selecione um tamanho.")
            return redirect(request.META.get('HTTP_REFERER', 'lista_camisetas'))

        camiseta = get_object_or_404(Camiseta, id=camiseta_id)  

        item = {
            'camiseta_id': camiseta.id, 
            'nome': camiseta.nome,
            'modelo': modelo,
            'tamanho': tamanho,
            'quantidade': 1
        }

        carrinho = request.session.get('carrinho', [])

        # Adiciona o item apenas se ele ainda não estiver no carrinho
        existe = any(
            i['camiseta_id'] == camiseta.id and i['modelo'] == modelo and i['tamanho'] == tamanho
            for i in carrinho
        )

        if not existe:
            carrinho.append(item)

        request.session['carrinho'] = carrinho
        request.session.modified = True

        return redirect('ver_carrinho')

    return redirect('lista_camisetas')


def remover_do_carrinho(request, camiseta_id, modelo, tamanho):
    carrinho = request.session.get('carrinho', [])

    carrinho = [
        item for item in carrinho
        if not (
            item['camiseta_id'] == camiseta_id and
            item['modelo'] == modelo and
            item['tamanho'] == tamanho
        )
    ]

    request.session['carrinho'] = carrinho
    request.session.modified = True

    return redirect('ver_carrinho')

def incrementar_item(request, camiseta_id, modelo, tamanho):
    carrinho = request.session.get('carrinho', [])
    camiseta = get_object_or_404(Camiseta, id=camiseta_id)
    estoque_disponivel = camiseta.estoque.get(modelo, {}).get(tamanho, 0)

    for item in carrinho:
        if item['camiseta_id'] == camiseta.id and item['modelo'] == modelo and item['tamanho'] == tamanho:
            atual = item.get('quantidade', 1)
            if atual >= estoque_disponivel:
                messages.error(request, f"Estoque insuficiente: só temos {estoque_disponivel} unidade(s) de {camiseta.nome} ({modelo} - {tamanho.upper()}).")
                break
            item['quantidade'] = atual + 1
            break

    request.session['carrinho'] = carrinho
    request.session.modified = True
    return redirect('ver_carrinho')


def decrementar_item(request, camiseta_id, modelo, tamanho):
    carrinho = request.session.get('carrinho', [])

    for item in carrinho:
        if (item['camiseta_id'] == camiseta_id and
            item['modelo'] == modelo and
            item['tamanho'] == tamanho):
            item['quantidade'] = item.get('quantidade', 1) - 1

            if item['quantidade'] <= 0:
                carrinho.remove(item)
            break

    request.session['carrinho'] = carrinho
    request.session.modified = True
    return redirect('ver_carrinho')

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', [])
    itens = []
    total_geral = 0

    for item in carrinho:
        try:
            camiseta = Camiseta.objects.get(id=item['camiseta_id'])
            quantidade = item.get('quantidade', 1)
            preco_unitario = camiseta.preco_unitario(quantidade)
            subtotal = preco_unitario * quantidade

            itens.append({
                'camiseta': camiseta,
                'modelo': item['modelo'],
                'tamanho': item['tamanho'],
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
                'subtotal': subtotal
            })

            total_geral += subtotal
        except Camiseta.DoesNotExist:
            continue

    total_carrinho = sum(item.get('quantidade', 1) for item in carrinho)

    return render(request, 'blink/carrinho.html', {
        'itens': itens,
        'total_geral': total_geral,
        'total_carrinho': total_carrinho,
    })

def checkout(request):
    if request.method == "POST":
        email = request.POST.get("email")
        carrinho = request.session.get("carrinho", [])

        # Monta os produtos para o Stripe
        line_items = []          # Itens que vão para o Stripe Checkout
        carrinho_metadata = []   # Informações que vão nos metadados da Session

        # Para cada item no carrinho
        for item in carrinho:
            camiseta_id = item['camiseta_id']
            modelo = item['modelo']
            tamanho = item['tamanho']
            quantidade = item.get('quantidade', 1)

            # Busca a camiseta no banco
            camiseta = Camiseta.objects.get(id=camiseta_id)

            # Calcula o preço unitário correto (desconto automático para 3 ou mais)
            preco_unitario = camiseta.preco_unitario(quantidade)

            # Monta o produto para o Stripe
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f"{camiseta.nome} ({modelo} - {tamanho})",
                    },
                    'unit_amount': int(preco_unitario * 100),  # Stripe usa centavos
                },
                'quantity': quantidade,
            })

            # Monta o carrinho para salvar como metadata
            carrinho_metadata.append({
                'camiseta_id': camiseta.id,
                'modelo': modelo,
                'tamanho': tamanho,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
            })

        # Agora que todos os itens foram processados, cria a sessão Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=email,
            metadata={
                'carrinho': json.dumps(carrinho_metadata)  # Serializa o carrinho
            },
            success_url=request.build_absolute_uri('/sucesso/'),
            cancel_url=request.build_absolute_uri('/carrinho/'),
        )

        # Redireciona o cliente para o Checkout do Stripe
        return redirect(session.url, code=303)

    # Se alguém tentar acessar GET em /checkout/, redireciona para o carrinho
    return redirect('ver_carrinho')


def sucesso(request):
    # ID da sessão Stripe salvo no momento do checkout
    sid = request.session.pop("ultima_session_id", None)
    if not sid:
        return redirect("home") 

    # Pedido salvo pelo webhook
    pedido = Pedido.objects.filter(stripe_session_id=sid, pago=True).first()
    if not pedido:
        # Se o webhook ainda não rodou, pode exibir uma página "Processando…"
        return render(request, "blink/processando.html")

    # Limpa carrinho apenas visualmente
    request.session["carrinho"] = []
    request.session.modified = True
    
    return render(request, "blink/sucesso.html", {"pedido": pedido})

def home(request):
    camisetas = Camiseta.objects.all()
    carrinho = request.session.get('carrinho', [])
    total_carrinho = sum(item.get('quantidade', 0) for item in carrinho)

    return render(request, 'blink/home.html', {
        'camisetas': camisetas,
        'total_carrinho': total_carrinho,
    })

def produto(request, slug):
    camiseta = get_object_or_404(Camiseta, slug=slug)
    tamanhos = ["PP", "P", "M", "G", "GG", "XG"]
    carrinho = request.session.get('carrinho', [])
    total_carrinho = sum(item.get('quantidade', 1) for item in carrinho)

    context = {
        'camiseta': camiseta,
        'tamanhos': tamanhos,
        'total_carrinho': total_carrinho,
    }
    return render(request, 'camisetas/camiseta_slug.html', context)

def lista_camisetas(request):
    camisetas = Camiseta.objects.all()
    carrinho = request.session.get('carrinho', [])
    total_carrinho = sum(item.get('quantidade', 1) for item in carrinho)

    return render(request, 'camisetas/camisetas.html', {
        'camisetas': camisetas,
        'total_carrinho': total_carrinho,
    })

def meus_pedidos(request):
    pedidos = None
    email = ""

    if request.method == "POST":
        email = request.POST.get("email")
        pedidos = Pedido.objects.filter(email=email).order_by("-data")

    carrinho = request.session.get('carrinho', [])
    total_carrinho = sum(item.get('quantidade', 1) for item in carrinho)

    return render(request, 'blink/meus_pedidos.html', {
        'pedidos': pedidos,
        'email': email,
        'total_carrinho': total_carrinho,
    })

@csrf_exempt
def webhook_stripe(request):
    payload = request.body
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        if session.get('payment_status') == 'paid':
            email = session.get('customer_email')
            carrinho_json = session.get('metadata', {}).get('carrinho')

            if not carrinho_json:
                return JsonResponse({'error': 'Carrinho não encontrado nos metadados.'}, status=400)

            carrinho = json.loads(carrinho_json)

            # Cria o pedido
            pedido = Pedido.objects.create(
                email=email,
                total=session['amount_total'] / 100,
                status='processando',
                stripe_session_id=session['id'],
                pago=True
            )

            # Cria os itens do pedido e baixa o estoque
            for item in carrinho:
                camiseta_id = item.get('camiseta_id')
                modelo = item.get('modelo')
                tamanho = item.get('tamanho')
                quantidade = item.get('quantidade')
                preco_unitario = item.get('preco_unitario')

                if None in [camiseta_id, modelo, tamanho, quantidade, preco_unitario]:
                    continue  # pula itens inválidos

                camiseta = Camiseta.objects.get(id=camiseta_id)

                # Cria o item pedido
                ItemPedido.objects.create(
                    pedido=pedido,
                    camiseta=camiseta,
                    modelo=modelo,
                    tamanho=tamanho,
                    quantidade=quantidade,
                    preco_unitario=preco_unitario
                )

                # Diminui o estoque da camiseta
                camiseta.diminuir_estoque(modelo, tamanho, quantidade)

    return JsonResponse({'status': 'success'})