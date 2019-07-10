from django.urls import path

from .views import (
    CollectionGroupDetailView, join_group
)


app_name = "collection"
urlpatterns = [
    path(
        'sammelgruppe/<int:pk>/',
        CollectionGroupDetailView.as_view(),
        name='collectiongroup-detail'
    ),
    path(
        'sammelgruppe/<int:pk>/join/',
        join_group,
        name='collectiongroup-join'
    ),
]
