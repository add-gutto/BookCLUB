from django.conf import settings
import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView,
    PasswordResetConfirmView
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, FormView
)

from .forms import UserForm, AuthenticationForm, ProfileForm, EmailChangeForm
from .models import User, Profile, Seguidor





# ----------------------------
# Página inicial protegida
# ----------------------------
@login_required
def index(request):
    return render(request, "index.html")


# ----------------------------
# PERFIL
# ----------------------------

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "user/profile/index.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.get_object()
        seguindo_ids = self.request.user.seguindo.values_list('seguindo__id', flat=True)
        seguidores_ids = self.request.user.seguidores.values_list('usuario__id', flat=True)
        context['is_seguindo'] = perfil.id in seguindo_ids          # request.user já segue esse perfil?
        context['is_seguido_por'] = perfil.id in seguidores_ids    # esse perfil segue request.user?
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
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
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "user/user_list.html"
    context_object_name = "users"

    def test_func(self):
        return self.request.user.is_staff


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "user/user_detail.html"
    context_object_name = "user"


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "user/forms/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_rules"] = password_validators_help_text_html()
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        return redirect("user-profile", pk=user.pk)


class UserStatusActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect("user-list")


class UserAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_staff = not user.is_staff
        user.is_superuser = not user.is_superuser
        user.save()
        return redirect("user-list")


# ----------------------------
# Autenticação
# ----------------------------
class UserLoginView(LoginRequiredMixin, FormView):
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


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("home")


# ----------------------------
# Gerenciamento de Senhas
# ----------------------------
class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "user/forms/change_password.html"

    def get_success_url(self):
        return reverse_lazy("user-detail", kwargs={"pk": self.request.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_rules"] = password_validators_help_text_html()
        return context



class UserPasswordResetView(LoginRequiredMixin, PasswordResetView):
    form_class = PasswordResetForm
    template_name = "user/forms/password_reset.html"
    subject_template_name = "user/email/resetar_senha_email.txt"
    email_template_name = "user/email/resetar_senha_email.html"
    html_email_template_name = "user/email/resetar_senha_email.html"
    success_url = reverse_lazy("login")

    def get_users(self, email):
        active_users = User.objects.filter(email__iexact=email)
        return [user for user in active_users if user.has_usable_password()]

    def get_email_context(self, user):
        return {
            "APP_NAME": settings.APP_NAME,
            "user": user
        }

    def form_valid(self, form):
        for user in self.get_users(form.cleaned_data["email"]):
            form.save(
                request=self.request,
                use_https=self.request.is_secure(),
                from_email=None,
                email_template_name=self.email_template_name,
                subject_template_name=self.subject_template_name,
                html_email_template_name=self.html_email_template_name,
                extra_email_context=self.get_email_context(user),
            )
        return HttpResponseRedirect(self.success_url) 


class UserPasswordResetConfirmView(LoginRequiredMixin, PasswordResetConfirmView):
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


@login_required
def seguir_usuario(request, user_id):
    usuario_a_seguir = get_object_or_404(User, pk=user_id)

    if usuario_a_seguir == request.user:
        return redirect("user-profile", pk=user_id)

    relacionamento, criado = Seguidor.objects.get_or_create(
        usuario=request.user,
        seguindo=usuario_a_seguir
    )
    if not criado:
        relacionamento.delete()

    return redirect("user-profile", pk=user_id)

# ----------------------------
# Gerenciamento de Troca de Email
# ----------------------------

# ----------------------------
# Pesquisa de Usuários
# ----------------------------
@login_required
def search_users(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query", "").strip()
    else:
        query = ""

    users = []
    if query:
        users = User.objects.filter(name__icontains=query) | User.objects.filter(email__icontains=query)
        users = users.distinct()

    return render(request, 'user/partials/search.html', {
        'users': users,
        'query': query
    })
