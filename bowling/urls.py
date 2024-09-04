from django.urls import path,include
from .views import BowlingViewSet
urlpatterns = [
    path('list/',BowlingViewSet.as_view({'get':'list'}),name='bowling_list'),
    path('add/',BowlingViewSet.as_view({'post':'create'}),name='add_bowling'),
    path('<int:pk>/',BowlingViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='bowling_details'),
]