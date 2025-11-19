from django import forms
from .models import Grupo


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ["nome", "descricao", "privado", "imagem"]
