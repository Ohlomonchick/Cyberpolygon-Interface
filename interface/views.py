from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from interface.models import Lab
from interface.forms import LabAnswerForm


class LabDetailView(DetailView):
    model = Lab

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = LabAnswerForm()
        context["submitted"] = False
        ans = self.request.GET.get("answer_flag")
        if ans:
            if ans == context["object"].answer_flag:
                context["submitted"] = True
            else:
                context["form"].fields["answer_flag"].label = "Неверный флаг!"

        return context


class LabListView(ListView):
    model = Lab



