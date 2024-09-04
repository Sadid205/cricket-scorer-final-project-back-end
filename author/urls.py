from django.urls import path,include
from .views import RegistrationView,activate,AuthorLoginApiView,AuthorLogoutApiView

urlpatterns=[
    path('register/',RegistrationView.as_view(),name="register"),
    path('active/<uid64>/<token>/',activate,name="activate"),
    path('login/',AuthorLoginApiView.as_view(),name="login"),
    path('logout/',AuthorLogoutApiView.as_view(),name="logout"),
]