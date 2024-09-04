from django.urls import path,include
from .views import MatchViewSet,StartMatchView,SelectOpeningPlayerView,UpdateScoreView,GetOversListView,SelectNewBowlerView,StartSecondInningsView
urlpatterns = [
    path('list/',MatchViewSet.as_view({'get':'list'}),name='match_list'),
    path('add/',MatchViewSet.as_view({'post':'create'}),name='add_match'),
    path('<int:pk>/',MatchViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='match_details'),
    path('start/',StartMatchView.as_view(),name="start_match"),
    path('select_opening_player/',SelectOpeningPlayerView.as_view(),name="select_opening_player"),
    path('update_score/',UpdateScoreView.as_view(),name="score_update"),
    path('get_overs_list/<int:match_id>/',GetOversListView.as_view(),name="get_overs_list"),
    path('add_new_over/',SelectNewBowlerView.as_view(),name="add_new_over"),
    path('start_second_innings/',StartSecondInningsView.as_view(),name="start_second_innings"),
]