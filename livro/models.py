from django.db import models
from user.models import User


class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    capa = models.URLField(blank=True, null=True)
    ano_publicacao = models.CharField(max_length=20, blank=True, null=True)
    identificador_api = models.CharField(
        max_length=50, unique=True
    )

    def __str__(self):
        return self.titulo


class Resenha(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resenhas"
    )
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name="resenhas"
    )

    nota = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Avaliação de 1 a 5 estrelas."
    )

    comentario = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "livro")  # usuário só pode avaliar 1x
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario.username} avaliou {self.livro.titulo} com {self.nota} estrelas"
