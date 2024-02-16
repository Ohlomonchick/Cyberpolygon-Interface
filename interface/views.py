from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import logging
from interface.models import Lab, Answers, User, Platoon
from interface.forms import LabAnswerForm

from django.contrib.auth import login, authenticate
from interface.forms import SignUpForm
from django.shortcuts import render, redirect


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



def registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        platoon = int(request.POST.get('platoon'))
        if not Platoon.objects.filter(number = platoon).exists():
            Platoon.objects.create(number = platoon)
        platoon = Platoon.objects.get(number = platoon)
        form.platoon = platoon
        if form.is_valid():
            usname = request.POST.get('name') + " " + request.POST.get('second_name')
            if User.objects.filter(username = usname).exists():
                user = User.objects.get(username = usname)
            else:
                user = form.save(commit = False)
                user.username = usname
                user = form.save()
            authenticate(user)
            login(request, user)
            return redirect('/cyberpolygon/')
    else:
        form = SignUpForm()
    return render(request, 'registration/reg_user.html', {'form': form})
