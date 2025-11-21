from django.db import models
from user.models import User
from livro.models import Livro


class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    privado = models.BooleanField(default=False)
    administrador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grupos_administrados"
    )
    imagem = models.ImageField(upload_to="grupos/", blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    membros = models.ManyToManyField(
        User,
        through="GrupoMembro",
        related_name="grupos_participando",
        blank=True
    )

    def __str__(self):
        return self.nome


class GrupoMembro(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="membros_info"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grupos_info"
    )
    data_entrada = models.DateTimeField(auto_now_add=True)

    # ordem obrigatoriamente precisa permitir null
    ordem = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('grupo', 'usuario')
        ordering = ['ordem']

    def save(self, *args, **kwargs):
        if self.ordem is None:
            ultimo = GrupoMembro.objects.filter(grupo=self.grupo).count()
            self.ordem = ultimo + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} → {self.grupo} (#{self.ordem})"


class Topico(models.Model):
    grupo = models.ForeignKey(
        "Grupo",
        on_delete=models.CASCADE,
        related_name="topicos"
    )
    livro = models.ForeignKey(
        Livro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topicos"
    )
    nome = models.CharField(max_length=150)
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="topicos_criados"
    )

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f"{self.nome} — {self.grupo.nome}"

    # Métodos úteis
    def qtd_mensagens(self):
        return self.mensagens.count()

    def tem_spoilers(self):
        return self.mensagens.filter(is_spoiler=True).exists()

    def ultima_mensagem(self):
        return self.mensagens.order_by('-criado_em').first()


class Mensagem(models.Model):
    topico = models.ForeignKey(
        Topico,
        on_delete=models.CASCADE,
        related_name="mensagens"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mensagens"
    )
    conteudo = models.TextField()
    imagem = models.ImageField(upload_to="mensagem/", blank=True, null=True)
    capitulo = models.PositiveIntegerField(null=True, blank=True)
    is_spoiler = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]

    def save(self, *args, **kwargs):
        if self.capitulo is not None:
            self.is_spoiler = True
        super().save(*args, **kwargs)

    def __str__(self):
        user = self.usuario.username if self.usuario else "Anônimo"
        return f"{user} — {self.topico} ({'spoiler' if self.is_spoiler else 'normal'})"
