from django.urls import path

from interface.views import LabDetailView, LabListView

urlpatterns = [
    path("<slug:slug>/", LabDetailView.as_view(), name="lab-detail"),
    path("", LabListView.as_view(), name="lab-list")
]