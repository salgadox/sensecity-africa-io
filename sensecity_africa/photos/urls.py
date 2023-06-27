from django.urls import path

from . import views

app_name = "photos"
urlpatterns = [
    # path("", views.PhotoListView.as_view(), name="list"),
    path("", views.PhotoSlideShowView.as_view(), name="slideshow"),
    path("list", views.PhotoListView.as_view(), name="list"),
    path("tag/<slug:tag_slug>", views.PhotoListView.as_view(), name="tag"),
    path("city/<slug:city_slug>", views.PhotoListView.as_view(), name="city"),
    path("country/<slug:country_slug>", views.PhotoListView.as_view(), name="country"),
    path(
        "tag-autocomplete/",
        views.TagAutocomplete.as_view(),
        name="tag-autocomplete",
    ),
    path(
        "country/",
        views.CountryAutocomplete.as_view(),
        name="country",
    ),
    path(
        "city/",
        views.CityAutocomplete.as_view(),
        name="city",
    ),
    path("<int:pk>/", views.PhotoDetailView.as_view(), name="detail"),
    path(
        "upload/",
        views.PhotoCreateView.as_view(),
        name="upload",
    ),
]
