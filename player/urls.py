from django.urls import path,include
from .views import PlayerViewSet


urlpatterns = [
    path('list/',PlayerViewSet.as_view({'get':'list'}),name="player_list"),
    path('add/',PlayerViewSet.as_view({'post':'create'}),name='add_player'),
    path('<int:pk>/',PlayerViewSet.as_view({'put':'update','get':'retrieve','delete':'destroy','patch':'partial_update'}),name='player_details'),
]