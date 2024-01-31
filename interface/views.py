from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from interface.models import Lab, Answers
from interface.forms import LabAnswerForm


class LabDetailView(DetailView):
    model = Lab

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = LabAnswerForm()
        context["submitted"] = False
        if self.request.user.is_authenticated:
            answered = Answers.objects.filter(lab=context["object"], user=self.request.user).first()
            if answered is None:
                answer = self.request.GET.get("answer_flag")
                if answer:
                    if answer == context["object"].answer_flag:
                        context["submitted"] = True
                        answer_object = Answers(lab=context["object"], user=self.request.user)
                        answer_object.save()
                    else:
                        context["form"].fields["answer_flag"].label = "Неверный флаг!"
            else:
                context["submitted"] = True

        return context


class LabListView(ListView):
    model = Lab



