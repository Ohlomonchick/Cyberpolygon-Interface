from collections import defaultdict

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from interface.models import *
from interface.forms import LabAnswerForm

from django.contrib.auth import login, authenticate
from interface.forms import SignUpForm, ChangePasswordForm
from django.shortcuts import render, redirect
from django.utils import timezone
from interface.eveFunctions import pf_login, create_directory, create_user, logout, change_user_password

from interface.serializers import *
from rest_framework import viewsets


class LabDetailView(DetailView):
    model = Lab


class LabListView(ListView):
    model = Lab


class CompetitionListView(ListView):
    model = Competition
    template_name = 'interface/competition_list.html'
    context_object_name = 'competitions'

    def get_queryset(self):
        queryset = Competition.objects.order_by("-start").filter(finish__gt=timezone.now())
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                competition_users__user=self.request.user
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        competitions = context["competitions"]
        kkz_groups = defaultdict(list)

        for comp in competitions:
            if comp.kkz:
                kkz_groups[comp.kkz].append(comp)

        context["kkz_groups"] = dict(kkz_groups)

        return context


class CompetitionHistoryListView(CompetitionListView):
    template_name = "interface/competition_history_list.html"

    def get_queryset(self):
        queryset = Competition.objects.order_by("-start").filter(finish__lte=timezone.now())
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                competition_users__user=self.request.user
            )
        return queryset


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'interface/competition_detail.html'

    def set_submitted(self, context):
        context["form"] = LabAnswerForm()
        context["submitted"] = False
        lab = self.object.lab
        if self.request.user.is_authenticated:
            competition = context["object"]
            context["available"] = competition.finish > timezone.now()
            context["issue"] = competition
            answers = Answers.objects.filter(
                lab=competition.lab,
                user=self.request.user,
                lab_task=None,
                datetime__lte=competition.finish,
                datetime__gte=competition.start
            ).first()
            if answers is None:
                answer = self.request.GET.get("answer_flag")
                if answer:
                    if answer == lab.answer_flag:
                        competition2user = Competition2User.objects.get(
                            competition=competition,
                            user=self.request.user
                        )
                        competition2user.done = True
                        context["done"] = True
                        competition2user.save()
                        context["submitted"] = True
                        answer_object = Answers(lab=lab, user=self.request.user, datetime=timezone.now())
                        answer_object.save()
                    else:
                        context["form"].fields["answer_flag"].label = "Неверный флаг!"
            else:
                context["submitted"] = True

            if context['submitted']:
                context['available'] = False

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = context["object"]
        context = self.set_submitted(context)

        if self.request.user.is_staff:
            solutions = Answers.objects.filter(
                lab=competition.lab,
                user__platoon__in=competition.platoons.all(),
                datetime__lte=competition.finish,
                datetime__gte=competition.start
            ).order_by('datetime').values()
            context["solutions"] = solutions

            if not str(competition.participants).isnumeric() or int(competition.participants) == 0:
                context["progress"] = 100
            else:
                context["progress"] = round(len(solutions) / int(competition.participants) * 100)

        if self.request.user.is_authenticated:
            try:
                competition2user = Competition2User.objects.get(competition=competition, user=self.request.user)
                assigned_tasks = competition2user.tasks.all()
            except Competition2User.DoesNotExist:
                assigned_tasks = []

            context["assigned_tasks"] = assigned_tasks

        context["object"] = competition
        context["button"] = (timezone.now() - competition.start).total_seconds() < 0

        return context


class PlatoonDetailView(DetailView):
    model = Platoon
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        user_list = User.objects.filter(platoon=context["platoon"]).exclude(username="admin")
        context["user_list"] = user_list
        competitions = {}
        comps = Competition.objects.filter(platoons=context["platoon"])
        for comp in comps:
            if (comp.finish - timezone.now()).seconds < 0:
                competitions[comp] = False
            else:
                competitions[comp] = True
        context["competitions"] = competitions
        logging.debug(context)
        logging.debug(competitions)
        return context


class PlatoonListView(ListView):
    model = Platoon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        platoons_progress = {}
        for platoon in context["object_list"]:
            if platoon.number != 0:
                platoons_progress[platoon] = PlatoonListView.get_platoon_progress(platoon)

        context["object_list"] = platoons_progress
        logging.debug(context)
        return context

    @staticmethod
    def get_platoon_progress(platoon):
        progress_dict = {"total": 0, "submitted": 0, "progress": 0}
        user_list = User.objects.filter(platoon=platoon).exclude(username="admin")
        for user in user_list:
            progress_dict["total"] += Competition2User.objects.filter(user=user).count()
            progress_dict["submitted"] += (
                Answers.objects.filter(user=user)
                .values("lab")
                .distinct()
                .count()
            )
        if progress_dict["total"] == 0:
            progress_dict["progress"] = 0
        else:
            progress_dict["progress"] += int((progress_dict["submitted"] / progress_dict["total"]) * 100)

        return progress_dict


class UserDetailView(DetailView):
    model = User
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.filter(username="admin").first()
        issues = Competition2User.objects.filter(user=context["object"])
        object_list = issues
        context["object_list"] = object_list
        total = len(issues)
        context["total"] = total
        context["submitted"] = (
            Answers.objects.filter(user=context["object"])
            .values("lab")
            .distinct()
            .count()
        )
        if total == 0:
            progress = 100
        else:
            progress = int((context["submitted"] / total) * 100)
        context["progress"] = progress
        logging.debug(context)
        return context

def registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        platoon = int(request.POST.get('platoon'))
        platoon = Platoon.objects.get(id=platoon)
        form.platoon = platoon
        if form.is_valid():
            usname = request.POST.get('last_name') + "_" + request.POST.get('first_name')
            passwd = request.POST.get('password')
            user = authenticate(username=usname, password=passwd)
            if user:
                if user.platoon == platoon:
                    login(request, user)
                    if passwd == "test.test":
                        return redirect('registration/change_password')
                    return redirect('/cyberpolygon/labs')
                else:
                    form.add_error("platoon", "В этом взводе нет такого пользователя")
            else:
                form.add_error("password", "Неправильный логин или пароль")
    else:
        form = SignUpForm()
    return render(request, 'registration/reg_user.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if request.POST.get('password1') == request.POST.get('password2') and request.POST.get('password1') != "":
            user = request.user
            user.set_password(request.POST.get('password1'))
            user.save()
            login(request, user)
            url = "http://172.18.4.160"
            Login = 'pnet_scripts'
            Pass = 'eve'
            cookie, xsrf = pf_login(url, Login, Pass)
            change_user_password(url, cookie, xsrf, user.pnet_login, request.POST.get('password1'))
            logout(url)
            return redirect('/cyberpolygon/labs')
        else:
            form = ChangePasswordForm()
    else:
        form = ChangePasswordForm()
    return render(request, 'registration/change_password.html', {'form': form})


class AnswerAPIView(viewsets.ModelViewSet):
    queryset = Answers.objects.all()
    serializer_class = AnswerSerializer
