from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, FormView
)

from .forms import UserForm, AuthenticationForm, ProfileForm
from .models import User, Profile


# ----------------------------
# Página inicial protegida
# ----------------------------
@login_required
def index(request):
    return render(request, "index.html")


# ----------------------------
# PERFIL
# ----------------------------
class UserProfileView(DetailView):
    model = User
    template_name = "user/profile/index.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))


class EditProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "user/profile/form_profile.html"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("user-profile", kwargs={"pk": self.object.user.pk})


# ----------------------------
# CRUD de Usuários
# ----------------------------
class UserListView(ListView):
    model = User
    template_name = "user/user_list.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    model = User
    template_name = "user/user_detail.html"
    context_object_name = "user"


class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = "user/forms/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_rules"] = password_validators_help_text_html()
        return context

    def form_valid(self, form):
        # Cria o usuário mas ainda não salva totalmente
        user = form.save(commit=False)
        user.is_active = True
        user.save()

        # 🔹 Cria o perfil automaticamente associado a esse usuário
        Profile.objects.create(user=user)

        # Faz login automático
        login(self.request, user)

        # Redireciona para o perfil do usuário
        return redirect("user-profile", pk=user.pk)


class UserStatusActiveView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect("user-list")


class UserAdminView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_staff = not user.is_staff
        user.is_superuser = not user.is_superuser
        user.save()
        return redirect("user-list")


# ----------------------------
# Autenticação
# ----------------------------
class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = "user/forms/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            form.add_error(None, "Conta desativada. Contate o administrador.")
            return self.form_invalid(form)
        login(self.request, user)
        return super().form_valid(form)


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


# ----------------------------
# Gerenciamento de Senhas
# ----------------------------
class UserPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "user/forms/change_password.html"

    def get_success_url(self):
        return reverse_lazy("user-detail", kwargs={"pk": self.request.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_rules"] = password_validators_help_text_html()
        return context


class UserPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = "user/forms/password_reset.html"
    subject_template_name = "user/email/resetar_senha_email.txt"
    email_template_name = "user/email/resetar_senha_email.html"
    html_email_template_name = "user/email/resetar_senha_email.html"
    success_url = reverse_lazy("password_reset_done")

    extra_email_context = {"APP_NAME": settings.APP_NAME}


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = "user/forms/password_reset_confirm.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Senha redefinida com sucesso! Você já pode fazer login.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_rules"] = password_validators_help_text_html()
        return context


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "user/forms/password_reset_complete.html"
