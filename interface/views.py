from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import logging
from interface.models import *
from interface.forms import LabAnswerForm

from django.contrib.auth import login, authenticate
from interface.forms import SignUpForm, ChangePasswordForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from interface.eveFunctions import pf_login, create_directory, create_user, logout

from interface.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
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
            now = timezone.now()
            issuedLab = IssuedLabs.objects.filter(lab=context["object"], user=request.user, end_date__gte=now,
                                                  date_of_appointment__lte=now).exclude(done=True).first()
            context["issue"] = issuedLab

            competition = False
            answers = None
            if "competition" in context.keys():
                competition = context["competition"]
                context["issue"] = competition
                answers = Answers.objects.filter(lab=context["object"], user=request.user, datetime__lte=competition.finish,
                                                 datetime__gte=competition.start).first()
            if issuedLab or competition and (answers is None):
                if issuedLab:
                    context["available"] = True if issuedLab.end_date > timezone.now() else False
                else:
                    context["available"] = True if competition.finish > timezone.now() else False

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
        queryset = Competition.objects.order_by("-start").all()
        if not self.request.user.is_staff:
            current_time = timezone.now()
            queryset = queryset.filter(
                platoons__in=[self.request.user.platoon]
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

class CompetitionDetailView(DetailView):
    model = Competition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = context["object"]
        context["object"] = competition.lab
        context["competition"] = competition
        context = LabDetailView.set_submitted(context, self.request)

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

        context["object"] = competition
        context["button"] = True if (timezone.now() - competition.start).total_seconds() < 0 else False

        return context


class PlatoonDetailView(DetailView):
    model = Platoon
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            progress_dict["total"] += len(IssuedLabs.objects.filter(user=user))
            progress_dict["submitted"] += len(IssuedLabs.objects.filter(user=user).exclude(done=False))
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
        issues = IssuedLabs.objects.filter(user=context["object"])
        object_list = issues
        context["object_list"] = object_list
        total = len(issues)
        context["total"] = total
        submitted = len(IssuedLabs.objects.filter(user=context["object"]).exclude(done=False))
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
            create_directory(url, "/Practice work/Test_Labs/api_test_dir", user.username, cookie)
            create_user(url, user.username, request.POST.get('password1'), '1', cookie)
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


# Хардкодный ответ (генерация потом)
hardcode = r"""/testdir/ 1 1 1 1 1 1 1 1 1 1
./ Горяиновd1 drwxrwxrwxm-- admin admin Секретно:Низкий:Нет:0x0
Горяиновd1/ Горяиновd2 drwxrwx---m-- admin admin Секретно:Низкий:Нет:0x0
Горяиновd1/ Горяиновf1 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0
Горяиновd1/ Горяиновf3 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0"""


#

def create_var_text(text, second_name):
    new_var = rf"""/testdir/ 1 1 1 1 1 1 1 1 1 1
./ {second_name}d1 drwxrwxrwxm-- admin admin Секретно:Низкий:Нет:0x0
{second_name}d1/ {second_name}d2 drwxrwx---m-- admin admin Секретно:Низкий:Нет:0x0
{second_name}d1/ {second_name}f1 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0
{second_name}d1/ {second_name}f3 -rwx------m-- admin admin Секретно:Низкий:Нет:0x0"""
    return new_var


@api_view(['GET'])
def start_lab(request):
    if request.method == 'GET':
        logging.debug(request.body)
        data = json.loads(request.body.decode('utf-8'))
        username = data.get("username", False)
        pnet_login = data.get("pnet_login", False)
        lab_name = data.get("lab")
        if (username or pnet_login) and lab_name:
            if username:
                user = User.objects.filter(username=username).first()
            else:
                user = User.objects.filter(pnet_login=pnet_login).first()
            lab = Lab.objects.filter(name=lab_name).first()
            logging.debug(lab)
            logging.debug(user)
            if user and lab:
                issue = IssuedLabs.objects.filter(lab_id=lab, user_id=user)
                # у нас на одного юзера не может назначаться несколько раз одна и та же лаба? пересдача с другим вариантом?
                if issue and not lab.answer_flag:
                    issue = issue[0]
                    data = {
                        "variant": issue.level.level_number,
                        "task": create_var_text(hardcode, user.last_name),
                        "tasks": [task.task_id for task in issue.tasks.all()]
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
        username = data.get("username", False)
        pnet_login = data.get("pnet_login", False)
        lab_name = data.get("lab")
        if (username or pnet_login) and lab_name:
            if username:
                user = User.objects.filter(username=username).first()
            else:
                user = User.objects.filter(pnet_login=pnet_login).first()
            lab = Lab.objects.filter(name=lab_name).first()
            if user and lab:
                issue = IssuedLabs.objects.filter(lab_id=lab, user_id=user).exclude(done=True).first()
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
