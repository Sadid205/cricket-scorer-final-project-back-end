from django.urls import path
from .views import PlayerViewSet,PlayerDetailsView


urlpatterns = [
    path('list/<int:team_id>/',PlayerViewSet.as_view({'get':'list'}),name="player_list"),
    path('player_details/<int:id>/',PlayerDetailsView.as_view(),name="player_detail"),
    path('add/',PlayerViewSet.as_view({'post':'create'}),name='add_player'),
    path('<int:pk>/',PlayerViewSet.as_view({'put':'update','get':'retrieve','delete':'destroy','patch':'partial_update'}),name='player_details'),
]