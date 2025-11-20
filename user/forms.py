from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django import forms
from .models import User, Profile
"""from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, 
    PasswordResetForm, AdminPasswordChangeForm, SetPasswordForm
) """

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "name"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'profile_picture', 'thumbnail']

class EmailChangeForm(forms.Form):
    old_email = forms.EmailField(label="E-mail atual", max_length=254)
    new_email = forms.EmailField(label="Novo e-mail", max_length=254)





User = get_user_model()

class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Usuário ou e-mail")

    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username_or_email and password:
            if "@" in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    raise forms.ValidationError("E-mail não encontrado.")
            else:
                username = username_or_email

            user = authenticate(self.request, username=username, password=password)

            if user is None:
                raise forms.ValidationError("Usuário ou senha inválidos.")

            # 🔹 GUARDA o user autenticado
            self.user_cache = user
            self.confirm_login_allowed(user)

        return self.cleaned_data

    # 🔹 PERMITE que a view acesse o user autenticado
    def get_user(self):
        return getattr(self, "user_cache", None)
