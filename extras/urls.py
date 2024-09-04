from django.urls import path,include
from .views import ExtrasViewSet
urlpatterns = [
    path('list/',ExtrasViewSet.as_view({'get':'list'}),name='extras_list'),
    path('add/',ExtrasViewSet.as_view({'post':'create'}),name='extras_add'),
    path('<int:pk>/',ExtrasViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='extras_details'),
]