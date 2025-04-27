from django.db import models
from django.utils.html import format_html

def estoque_padrao():
    tamanhos = {"PP": 0, "P": 0, "M": 0, "G": 0, "GG": 0, "XG": 0}
    return {"normal": tamanhos.copy(), "oversized": tamanhos.copy()}

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nome

class Camiseta(models.Model):
    MODELO_CHOICES = (
        ("normal", "Normal"),
        ("oversized", "Oversized"),
    )

    nome      = models.CharField(max_length=100)
    modelo    = models.CharField(max_length=20, choices=MODELO_CHOICES)
    estoque   = models.JSONField(default=estoque_padrao)  # {"normal": {...}, "oversized": {...}}
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    slug      = models.SlugField(unique=True)
    descricao = models.TextField(default="Descrição teste")
    ordem = models.PositiveIntegerField(default=0)

    # --- Métodos utilitários ---
    def preco_unitario(self, qtd: int = 1) -> float:
        """Retorna preço unitário conforme modelo e quantidade."""
        if self.modelo == "oversized":
            return 90 if qtd >= 3 else 95
        return 80 if qtd >= 3 else 85
    
    def diminuir_estoque(self, modelo, tamanho, quantidade): 
        if modelo not in self.estoque:
            raise ValueError(f"Modelo '{modelo}' não encontrado no estoque.")
        if tamanho not in self.estoque[modelo]:
            raise ValueError(f"Tamanho '{tamanho}' não encontrado no estoque do modelo '{modelo}'.")

        # Diminui o estoque, mas nunca deixa negativo
        self.estoque[modelo][tamanho] = max(0, self.estoque[modelo][tamanho] - quantidade)
        
        # Salva a camiseta com o novo estoque
        self.save()

    def imagem_preview(self):
        primeira = self.imagens.first()
        if primeira:
            return format_html('<img src="{}" width="50">', primeira.imagem.url)
        return "(sem imagem)"
    
    imagem_preview.short_description = "Preview"

    def __str__(self) -> str:
        return self.nome

    class Meta:
        ordering = ['ordem']  # CAMISETAS ORDENADAS POR ESSE CAMPO
        
class ImagemCamiseta(models.Model):
    camiseta = models.ForeignKey(Camiseta, related_name="imagens", on_delete=models.CASCADE)
    imagem   = models.ImageField(upload_to="camisetas/assets/")

    def __str__(self):
        return f"Imagem da {self.camiseta.nome}"

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
    ]

    email = models.EmailField(null=True, blank=True)  # <- NOVO
    data = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    pago = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.data.strftime('%d/%m/%Y')} - {self.email}"

class ItemPedido(models.Model):
    pedido         = models.ForeignKey(Pedido, related_name="itens", on_delete=models.CASCADE)
    camiseta       = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    modelo         = models.CharField(max_length=20)
    tamanho        = models.CharField(max_length=10)
    quantidade     = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario
