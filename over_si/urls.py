from django.urls import path,include
from .views import OverSIViewSet
urlpatterns = [
    path('list/',OverSIViewSet.as_view({'get':'list'}),name='si_over_list'),
    path('add/',OverSIViewSet.as_view({'post':'create'}),name='si_add_over'),
    path('<int:pk>/',OverSIViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='si_over_details'),
  
]