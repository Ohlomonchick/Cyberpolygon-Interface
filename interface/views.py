from django.views.generic.detail import DetailView

from interface.models import Lab
from interface.forms import LabAnswerForm


class LabDetailView(DetailView):
    model = Lab

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = LabAnswerForm()
        return context

