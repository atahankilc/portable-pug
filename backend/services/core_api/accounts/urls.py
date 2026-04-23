from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import JWKSView, RegisterView

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path(".well-known/jwks.json", JWKSView.as_view(), name="jwks"),
]
