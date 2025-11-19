from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Usuário base do sistema
class User(AbstractUser):
    name = models.CharField(max_length=150, blank=True)
    first_name = None
    last_name = None

    def __str__(self):
        return self.name or self.username


# Perfil complementar do usuário
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profiles/pictures/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="profiles/thumbnails/", blank=True, null=True)

    def __str__(self):
        return self.user.name or self.user.username

class Seguidor(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="seguindo", on_delete=models.CASCADE)
    seguindo = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="seguidores", on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "seguindo")  
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario} segue {self.seguindo}"