from django.urls import path,include
from .views import OverFIViewSet
urlpatterns = [
    path('list/',OverFIViewSet.as_view({'get':'list'}),name='fi_over_list'),
    path('add/',OverFIViewSet.as_view({'post':'create'}),name='fi_add_over'),
    path('<int:pk>/',OverFIViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='fi_over_details'),
  
]