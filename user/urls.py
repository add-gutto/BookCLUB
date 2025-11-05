from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    UserLoginView, UserLogoutView, UserPasswordChangeView,
    UserPasswordResetView, UserPasswordResetConfirmView, UserPasswordResetCompleteView,
    UserListView, UserDetailView, UserCreateView, 
    UserStatusActiveView, EditProfileView, UserProfileView, UserAdminView,
)
from .viewsAPI import (
    RegisterAPIView, LoginAPIView, LogoutAPIView, ChangePasswordAPIView,
    PasswordResetRequestAPIView, ProfileAPIView
)

urlpatterns = [
    # ----------------------------
    # API (REST)
    # ----------------------------
    path('api/signup/', RegisterAPIView.as_view(), name='api-signup'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('api/profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('api/password/change/', ChangePasswordAPIView.as_view(), name='api-change-password'),
   path('api/password/reset/request/', PasswordResetRequestAPIView.as_view(), name='api-password-reset-request'),


    # ----------------------------
    # Views HTML
    # ----------------------------
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('signup/', UserCreateView.as_view(), name='sign-up'),
    path('status/<int:pk>/', UserStatusActiveView.as_view(), name='user-status'),
    path('status/admin/<int:pk>/', UserAdminView.as_view(), name='user-admin'),

    # Login/Logout
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # Senha
    path('password/reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/done/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/change/', UserPasswordChangeView.as_view(), name='change-password'),

    # Perfil
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('profile/editar/', EditProfileView.as_view(), name='editar_profile'),
]
