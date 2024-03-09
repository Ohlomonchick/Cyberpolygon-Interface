from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import logging
from interface.models import *
from interface.forms import LabAnswerForm

from django.contrib.auth import login, authenticate
from interface.forms import SignUpForm
from django.shortcuts import render, redirect
from django.utils import timezone

from interface.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from urllib.parse import unquote
import json

class LabDetailView(DetailView):
    model = Lab

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = LabDetailView.set_submitted(context, self.request)
        return context

    @staticmethod
    def set_submitted(context, request):
        context["form"] = LabAnswerForm()
        context["submitted"] = False
        lab = context["object"]
        if request.user.is_authenticated:
            answered = Answers.objects.filter(lab=lab, user=request.user).first()
            issuedLab = IssuedLabs.objects.filter(lab=context["object"], user=request.user).first()
            if answered is None:
                answer = request.GET.get("answer_flag")
                if answer:
                    if answer == lab.answer_flag:
                        context["submitted"] = True
                        answer_object = Answers(lab=lab, user=request.user, datetime=timezone.now())
                        if issuedLab:
                            issuedLab.done = True
                            issuedLab.save()
                        answer_object.save()
                    else:
                        context["form"].fields["answer_flag"].label = "Неверный флаг!"
            else:
                context["submitted"] = True
        return context


class LabListView(ListView):
    model = Lab

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            labs = []
            issues = IssuedLabs.objects.filter(user=self.request.user).exclude(done=True)
            for issue in issues:
                labs.append(issue.lab)
            labs_set = set(labs)
            object_list = labs_set
            context["object_list"] = object_list
        logging.debug(context)
        return context


class CompetitionListView(ListView):
    model = Competition

    def get_queryset(self):
        queryset = []
        if self.request.user.is_authenticated:
            queryset = Competition.objects.all()
            if not self.request.user.is_staff:
                queryset = queryset.filter(platoons__in=[self.request.user.platoon])
            queryset.order_by("start")
        return queryset


class CompetitionDetailView(DetailView):
    model = Competition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["available"] = True
        if not self.request.user.is_staff:
            if timezone.now() < context["object"].start or timezone.now() > context["object"].finish:
                context["available"] = False
                return context

        competition = context["object"]
        context["object"] = competition.lab
        context = LabDetailView.set_submitted(context, self.request)

        if self.request.user.is_staff:
            solutions = Answers.objects.filter(
                lab=competition.lab,
                user__platoon__in=competition.platoons.all()
            ).order_by('datetime').values()
            pos = 1
            for solution in solutions:
                user = User.objects.get(pk=solution["user_id"])
                solution["user"] = user
                solution["pos"] = str(pos)
                pos += 1

            context["solutions"] = solutions

        context["object"] = competition
        context["delta"] = CompetitionDetailView.get_timer(context["object"])

        return context

    @staticmethod
    def get_timer(competition):
        delta = (competition.finish - timezone.now()).seconds
        seconds = delta % 60
        delta //= 60
        minutes = delta % 60
        hours = delta // 60

        out = {"hours": hours, "minutes": minutes, "seconds": seconds}
        for key, value in out.items():
            n_value = str(value)
            n_value = (2 - len(n_value)) * "0" + n_value
            out[key] = n_value
        return out


class PlatoonDetailView(DetailView):
    model = Platoon
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_list = User.objects.filter(platoon = context["platoon"]).exclude(username = "admin")
        context["user_list"] = user_list
        competitions ={}
        comps = Competition.objects.filter(platoons = context["platoon"])
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
            platoons_progress[platoon] = {"total":0, "submitted":0, "progress":0}
            user_list = User.objects.filter(platoon = platoon).exclude(username = "admin")
            for user in user_list:
                platoons_progress[platoon]["total"] += len(IssuedLabs.objects.filter(user = user))
                platoons_progress[platoon]["submitted"] += len(IssuedLabs.objects.filter(user = user).exclude(done = False))
            if platoons_progress[platoon]["total"] == 0:
                platoons_progress[platoon]["progress"] = 100
            else:
                platoons_progress[platoon]["progress"] += int(platoons_progress[platoon]["submitted"] / platoons_progress[platoon]["total"]) * 100
        context["object_list"] = platoons_progress
        logging.debug(context)
        return context


class UserDetailView(DetailView):
    model = User
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.filter(username = "admin").first()
        issues = IssuedLabs.objects.filter(user = context["object"])
        object_list = issues
        context["object_list"] = object_list
        total = len(issues)
        context["total"] = total
        submitted = len(IssuedLabs.objects.filter(user = context["object"]).exclude(done = False))
        context["submitted"] = submitted
        if total == 0:
            progress = 100
        else:
            progress = int((submitted / total) * 100)
        context["progress"] = progress
        logging.debug(context)
        return context


def registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        platoon = int(request.POST.get('platoon'))
        platoon = Platoon.objects.get(id = platoon)
        form.platoon = platoon
        if form.is_valid():
            usname = request.POST.get('name') + " " + request.POST.get('second_name')
            if User.objects.filter(username = usname, platoon = platoon.id).exists():
                user = User.objects.get(username = usname, platoon = platoon.id)
                authenticate(user)
                login(request, user)
                return redirect('/cyberpolygon/labs')
            else:
                form = SignUpForm()
    else:
        form = SignUpForm()
    return render(request, 'registration/reg_user.html', {'form': form})


class AnswerAPIView(viewsets.ModelViewSet):
    queryset = Answers.objects.all()
    serializer_class = AnswerSerializer




# Хардкодный ответ (генерация потом)
hardcode = r"""/testdir/ 1 1 1 1 1 1 1 1 1 1
./ d1 drwxrwxrwxm-- admin admin Секретно:Низкий:Нет:0x0
d1/ d2 drwxrwx---m-- admin admin Секретно:Низкий:Нет:0x0
d1/ f1 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0
d1/ f3 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0"""
# 

@api_view(['GET'])
def start_lab(request):
    if request.method == 'GET':
        logging.debug(request.body)
        data = json.loads(request.body.decode('utf-8'))
        username = data.get("username")
        lab_name = data.get("lab")
        if username and lab_name:
            user = User.objects.filter(username = username).first()
            lab = Lab.objects.filter(name = lab_name).first()
            if user and lab:
                issue = IssuedLabs.objects.filter(lab_id = lab, user_id = user)
                if issue:
                    data = {
                        "variant":1,
                        "task": hardcode
                    }
                    return JsonResponse(data)
                else:
                    return JsonResponse({'message': 'No such issue'}, status=status.HTTP_404_NOT_FOUND) 
            else:
                return JsonResponse({'message': 'User or lab does not exist'}, status=status.HTTP_404_NOT_FOUND) 
        else:
                return JsonResponse({'message': 'Wrong request format'}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['POST'])
def end_lab(request):
    if request.method == 'POST':
        logging.debug(request.body)
        data = json.loads(request.body.decode('utf-8'))
        username = data.get("username")
        lab_name = data.get("lab")
        if username and lab_name:
            user = User.objects.filter(username = username).first()
            lab = Lab.objects.filter(name = lab_name).first()
            if user and lab:
                issue = IssuedLabs.objects.filter(lab_id = lab, user_id = user).first()
                if issue and not lab.answer_flag and not issue.done:
                    ans = Answers(lab=lab, user=user, datetime=timezone.now())
                    ans.save()
                    issue.done = True
                    issue.save()
                    return JsonResponse({'message': 'Task finished'})
                else:
                    return JsonResponse({'message': 'No such issue'}, status=status.HTTP_404_NOT_FOUND) 
            else:
                return JsonResponse({'message': 'User or lab does not exist'}, status=status.HTTP_404_NOT_FOUND) 
        else:
                return JsonResponse({'message': 'Wrong request format'}, status=status.HTTP_400_BAD_REQUEST)