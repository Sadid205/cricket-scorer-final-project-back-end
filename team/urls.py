from django.urls import path,include
# from rest_framework.routers import DefaultRouter
from .views import TeamView
# router = DefaultRouter()
# router.register('add',TeamView)
# urlpatterns = [
#     path('',include(router.urls))
# ]
urlpatterns = [
    path('list/<int:author_id>/',TeamView.as_view({'get':'list'}),name='teams_list'),
    path('add/',TeamView.as_view({'post':'create'}),name='add_team'),
    path('<int:pk>/',TeamView.as_view({'put':'update','delete':'destroy','patch':'partial_update','get':'retrieve'}),name='team_detail'),

]