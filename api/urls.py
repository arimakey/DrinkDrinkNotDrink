from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.create_user, name="create_user"),
    path('questions/next/<int:user_id>/', views.next_question, name="next_question"),
    path('questions/answer/<int:user_id>/', views.answer_question, name="answer_question"),
    path('feedback/<int:user_id>/', views.feedback, name="feedback"),
]
