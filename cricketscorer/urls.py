"""
URL configuration for cricketscorer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('teams/',include('team.urls')),
    path('player/',include('player.urls')),
    path('batsman/',include('batsman.urls')),
    path('batting/',include('batting.urls')),
    path('bowler/',include('bowler.urls')),
    path('bowling/',include('bowling.urls')),
    path('extras/',include('extras.urls')),
    path('fall_of_wickets/',include('fall_of_wickets.urls')),
    path('fielder/',include('fielder.urls')),
    path('fielding/',include('fielding.urls')),
    path('history/',include('history.urls')),
    path('match/',include('match.urls')),
    path('over_si/',include('over_si.urls')),
    path('over_fi/',include('over_fi.urls')),
    path('partnerships/',include('partnerships.urls')),
    path('author/',include('author.urls')),
]
