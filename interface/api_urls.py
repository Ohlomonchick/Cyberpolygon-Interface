from django.urls import path
from .views import AnswerAPIView, start_lab, end_lab
from .api import get_time, load_levels, load_tasks

urlpatterns = [
    path("answers", AnswerAPIView.as_view({'get': 'list', 'post': 'create'})),
    path("start", start_lab),
    path("end", end_lab),
    path('get_competition_time/<int:competition_id>/', get_time, name='get_time'),
    path('get_lab_levels/<str:lab_name>/', load_levels, name='load_levels'),
    path('lab_tasks/<str:lab_name>/', load_tasks, name='load_tasks'),
]