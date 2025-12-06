# user/signals.py
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from user.models import User
from .models import Profile

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == 'user':  # garante que só rode no app correto
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                name= "Administrador",
                username="admin",
                email="admin@gmail.com",
                password="admin123"
            )
            print("Admin padrão criado automaticamente.")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)