from django.db import models
from django.conf import settings

class Denuncia(models.Model):
    # Opções de status (para staff resolver)
    STATUS_CHOICES = [
        ('new','Nova'),
        ('in_progress','Em andamento'),
        ('resolved','Resolvida'),
        ('rejected','Rejeitada'),
    ]

    # Quem fez a denúncia (opcional)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='denuncias'
    )

    # Dados principais
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()

    # Alvo da denúncia (opcional e genérico)
    alvo_tipo = models.CharField(max_length=100, blank=True)  # Ex.: "Comentário", "Usuário", "Livro"
    alvo_id = models.CharField(max_length=100, blank=True)    # Ex.: ID do item

    # Status da denúncia (processamento)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'

    def __str__(self):
        return f"{self.titulo} — {self.get_status_display()}"