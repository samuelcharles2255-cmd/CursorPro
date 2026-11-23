from django.urls import path
from .views import FavoriteListCreateView

urlpatterns = [
    path("favorites/", FavoriteListCreateView.as_view(), name="favorite-list-create"),
]
