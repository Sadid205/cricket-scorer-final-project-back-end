from django.urls import path,include
from .views import BattingViewSets
urlpatterns = [
    path('list/',BattingViewSets.as_view({'get':'list'}),name='batting_list'),
    path('add/',BattingViewSets.as_view({'post':'create'}),name='create_batting'),
    path('<int:pk>/',BattingViewSets.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='batting_details'),
]