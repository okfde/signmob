from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt

from .views import (
    HomeView,
    CollectionGroupListView,
    CollectionGroupDetailView, join_group,
    CollectionLocationCreateView, CollectionLocationReportView,
    CollectionEventJoinView, cancel_event_membership
)


app_name = "collection"
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(
        'sammelgruppen/embed/',
        xframe_options_exempt(CollectionGroupListView.as_view()),
        name='collectiongroup-detail'
    ),
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
    path(
        'sammeltermin/absagen/<int:pk>/',
        cancel_event_membership,
        name='collectionevent-cancel'
    ),
]
