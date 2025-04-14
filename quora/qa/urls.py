from django.urls import path,re_path
from .views import QuestionAndAnswerRetriveUpdateDestroy, QuestionListCreateAPIView, QuestionRetrieveUpdateDestroyAPIView, AnswerLikeDislikesAPIView,Login,QuestionAndAnswerListCreate,Logout, UserCreationAPIView

urlpatterns = [
    path('questions/', QuestionListCreateAPIView.as_view(), name='question-list-create'),
    re_path(r'question/(?P<question_id>[0-9]+)/answers/$',QuestionAndAnswerListCreate.as_view(),name='question-answers-list/'),
    re_path(r'question/(?P<question_id>[0-9]+)/answers/(?P<pk>[0-9]+)/$',QuestionAndAnswerRetriveUpdateDestroy.as_view(),name='question-answers-list/'),
    re_path(r'questions/(?P<pk>[0-9]+)/$', QuestionRetrieveUpdateDestroyAPIView.as_view(), name='question-retrieve-update-destroy'),
    re_path(r'answers/(?P<pk>[0-9]+)/likes/$', AnswerLikeDislikesAPIView.as_view(), name='answer-like'),
    path("login/",Login.as_view(),name="user_login"),
    path("logout/",Logout.as_view(),name='user_logout'),
    path("users/",UserCreationAPIView.as_view(),name='user_creation')
]