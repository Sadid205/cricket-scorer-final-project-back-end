from django.urls import path,include
from .views import FielderViewSet
urlpatterns = [
    path('list/',FielderViewSet.as_view({'get':'list'}),name='fielder_list'),
    path('add/',FielderViewSet.as_view({'post':'create'}),name='add_fielder'),
    path('<int:pk>/',FielderViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='fielder_details'),
]