from django.contrib import admin
from .models import Topico, Mensagem
from user.models import Seguidor
# Register your models here.
admin.site.register(Topico)
admin.site.register(Mensagem)
admin.site.register(Seguidor)