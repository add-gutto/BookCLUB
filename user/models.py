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

