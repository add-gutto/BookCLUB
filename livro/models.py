from django.db import models

# Create your models here.
class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150, blank=True, null=True)
    ano_publicacao = models.CharField(max_length=10, blank=True, null=True)  # Google Books não é sempre inteiro
    descricao = models.TextField(blank=True, null=True)
    capa_url = models.URLField(blank=True, null=True)  

    def __str__(self):
        return self.titulo