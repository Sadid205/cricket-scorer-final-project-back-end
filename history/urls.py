from django.urls import path,include
from .views import HistoryViewSet
urlpatterns = [
    path('list/',HistoryViewSet.as_view({'get':'list'}),name='history_list'),
    path('add/',HistoryViewSet.as_view({'post':'create'}),name='add_history'),
    path('<int:pk>/',HistoryViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='history_details'),
]