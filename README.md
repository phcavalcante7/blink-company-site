# 🧢 Blink – Loja de Roupas Streetwear

Projeto completo de e-commerce desenvolvido com **Django**, integrando **Stripe**, controle de estoque, layout responsivo e organização profissional com Git.

---

## 🚀 Funcionalidades

- 🛒 Listagem de camisetas por categoria
- 🧾 Página de produto com variação de modelo e tamanhos
- 🧠 Preço dinâmico por quantidade
- 📦 Carrinho de compras com controle por sessão
- 💳 Checkout integrado com Stripe
- 📧 Webhook para registro de pedidos
- 📈 Painel admin com controle de estoque, imagens e descrição
- 📱 Site responsivo com layout inspirado em Brutal Kill e High Company
- 🔐 Segurança reforçada: dados sensíveis protegidos via `.env`

---

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Django 5.2](https://www.djangoproject.com/)
- [Stripe API](https://stripe.com/docs/api)
- [HTML/CSS (Tailwind-like)](https://tailwindcss.com/)
- [SQLite3](https://www.sqlite.org/index.html)
- Git (com `feature branches` e `rebase`)

---

## 📁 Como rodar localmente

```bash
git clone https://github.com/phcavalcante7/blink-company-site.git
cd blink-company-site
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
