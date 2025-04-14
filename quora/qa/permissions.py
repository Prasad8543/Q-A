
from rest_framework import permissions
from qa.models import Question,Answer

class UpdateDeleteQuestionPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        question_id = view.kwargs.get('pk')
        try:
            question = Question.objects.get(id=question_id)
            if question.created_by!=user:
                return False
            return True
        except Question.DoesNotExist:
            return False
        

class UpdateDeleteAnswerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        answer_id = view.kwargs.get('pk')
        question = view.kwargs.get("question_id")
        try:
            answer = Answer.objects.get(id=answer_id)
            if answer.created_by!=user:
                return False
            if question and answer.question_id!=int(question):
                return False
            return True
        except Answer.DoesNotExist:
            return False

