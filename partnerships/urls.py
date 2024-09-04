from django.urls import path,include
from .views import PartnershipsViewSet
urlpatterns = [
    path('list/',PartnershipsViewSet.as_view({'get':'list'}),name='partnerships_list'),
    path('add/',PartnershipsViewSet.as_view({'post':'create'}),name='add_partnerships'),
    path('<int:pk>/',PartnershipsViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='over_partnerships'),
]