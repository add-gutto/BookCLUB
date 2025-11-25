from django.db import models


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
