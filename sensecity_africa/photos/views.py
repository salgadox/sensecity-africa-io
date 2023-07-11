import json

from cities_light.models import City, Country
from dal import autocomplete
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from rest_framework import mixins, response, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .forms import PhotoForm
from .models import Photo, Tag
from .serializers import PhotoSerializer, PhotoUploadSerializer


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Tag.objects.none()
        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Country.objects.filter(continent="AF")

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = City.objects.all()

        country = self.forwarded.get("country", None)

        if country:
            qs = qs.filter(country=country)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class PhotoListView(generic.ListView):
    model = Photo
    context_object_name = "photos"
    paginate_by = 12
    ordering = ["-uploaded_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_kws = {}
        if "tag_slug" in self.kwargs:
            filter_kws["tags__slug__in"] = [self.kwargs["tag_slug"]]
        for kw in ["city_slug", "country_slug"]:
            try:
                filter_kws[f"{kw.split('_')[0]}__slug"] = self.kwargs[kw]
            except KeyError:
                pass
        queryset = queryset.filter(**filter_kws)
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if "tag_slug" in self.kwargs:
            title = _("Photos tagged with: ") + '"' + self.kwargs["tag_slug"] + '"'
        elif "city_slug" in self.kwargs:
            title = _("Photos from: ") + '"' + self.kwargs["city_slug"] + '"'
        elif "country_slug" in self.kwargs:
            title = _("Photos from: ") + '"' + self.kwargs["country_slug"] + '"'
        else:
            title = _("Photos")
        context["title"] = title

        # this will be useful in the template for pagination
        context["penultimate_page_number"] = context["paginator"].num_pages - 1

        return context


class PhotoSlideShowView(generic.ListView):
    model = Photo
    context_object_name = "photos"
    template_name = "photos/photo_slideshow.html"


class PhotoDetailView(generic.DetailView):
    model = Photo
    context_object_name = "photo"


class PhotoCreateView(SuccessMessageMixin, generic.CreateView):
    model = Photo
    form_class = PhotoForm

    success_message = _(
        "Your photo was uploaded successfully and is now awaiting moderation. Thank "
        "you!"
    )

    def get_success_url(self):
        return reverse("photos:list")


class PhotoViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    http_method_names = ["get", "post"]

    def create(self, request):
        data = json.loads(request.data["data"])
        data["image"] = request.data["image"]
        country = Country.objects.get(name=data["country"])
        city = City.objects.get(name=data["city"])
        data["country"] = country.pk
        data["city"] = city.pk
        serializer = PhotoUploadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            raise ValueError(serializer.errors)

        return response.Response(serializer.data)


class RandomPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PhotoSerializer
    http_method_names = ["get"]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # queryset = Photo.objects.order_by("?").all()
        # # rule of thumb:
        # # when there are 50 photos in the database, each photo will be shown for 10 s,
        # # whereas when there are 100 photos in the database, each photo will be shown
        # # for 5 s. then, considering that a request will be sent each 100s, if there
        # # are 50 photos in the database, we need to provide 10 photos as response,
        # # whereas if there are 100 photos in the database, we need to provide 20
        # # photos as response
        # return queryset[: int(len(queryset) / 5)]
        return Photo.objects.order_by("?").all()[:1]
