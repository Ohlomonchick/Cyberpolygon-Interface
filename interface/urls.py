from django.urls import path

from interface.views import LabDetailView

urlpatterns = [
    path("<slug:slug>/", LabDetailView.as_view(), name="lab-detail"),
]