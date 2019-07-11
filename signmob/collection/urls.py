from django.urls import path

from .views import (
    HomeView,
    CollectionGroupDetailView, join_group,
    CollectionLocationCreateView, CollectionLocationReportView,
    CollectionEventJoinView
)


app_name = "collection"
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(
        'sammelgruppe/<int:pk>/',
        CollectionGroupDetailView.as_view(),
        name='collectiongroup-detail'
    ),
    path(
        'sammelgruppe/<int:pk>/beitreten/',
        join_group,
        name='collectiongroup-join'
    ),

    path(
        'sammelort/erstellen/',
        CollectionLocationCreateView.as_view(),
        name='collectionlocation-create'
    ),
    path(
        'sammelort/<int:pk>/melden/',
        CollectionLocationReportView.as_view(),
        name='collectionlocation-report'
    ),


    path(
        'sammeltermin/<int:pk>/',
        CollectionEventJoinView.as_view(),
        name='collectionevent-join'
    ),
]
