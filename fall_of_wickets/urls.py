from django.urls import path,include
from .views import FallOfWicketsViewSet
urlpatterns = [
    path('list/',FallOfWicketsViewSet.as_view({'get':'list'}),name='fall_of_wickets_list'),
    path('add/',FallOfWicketsViewSet.as_view({'post':'create'}),name='add_fall_of_wickets'),
    path('<int:pk>/',FallOfWicketsViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='fall_of_wickets_details'),
]