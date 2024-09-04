from django.urls import path,include
from .views import BatsmanViewSet

urlpatterns = [
    path("list/",BatsmanViewSet.as_view({'get':'list'}),name='batsman_list'),
    path("add/",BatsmanViewSet.as_view({'post':'create'}),name='add_batsman'),
    path("<int:pk>/",BatsmanViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='batsman_details'),
]