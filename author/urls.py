from django.urls import path,include
from .views import RegistrationView,activate,AuthorLoginApiView,AuthorLogoutApiView
from .views import GoogleLogin

urlpatterns=[
    path('register/',RegistrationView.as_view(),name="register"),
    path('active/<uid64>/<token>/',activate,name="activate"),
    path('login/',AuthorLoginApiView.as_view(),name="login"),
    path('logout/',AuthorLogoutApiView.as_view(),name="logout"),
]

urlpatterns+= [
    path('api/auth/google/',GoogleLogin.as_view(),name='google_login'),
]