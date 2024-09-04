from django.urls import path,include
from .views import FieldingViewSet
urlpatterns = [
    path('list/',FieldingViewSet.as_view({'get':'list'}),name='fielding_list'),
    path('add/',FieldingViewSet.as_view({'post':'create'}),name='add_fielding'),
    path('<int:pk>/',FieldingViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='fielding_details'),
]