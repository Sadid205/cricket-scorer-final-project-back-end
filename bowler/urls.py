from django.urls import path,include
from .views import BowlerViewSet
urlpatterns = [
    path('list/',BowlerViewSet.as_view({'get':'list'}),name='bowler_list'),
    path('add/',BowlerViewSet.as_view({'post':'create'}),name='add_bowler'),
    path('<int:pk>/',BowlerViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='bowler_details'),
]