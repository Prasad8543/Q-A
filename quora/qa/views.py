from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .utils import get_jwt_token
from .permissions import UpdateDeleteAnswerPermission, UpdateDeleteQuestionPermission
from .models import ProgramUser, Question, Answer
from .serializers import ProgramUserSerializer, QuestionSerializer, AnswerSerializer, QuestionWithAnswersSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def get(self,request):
        return super(QuestionListCreateAPIView, self).get(request, format)
    
    def post(self,request):
        return super(QuestionListCreateAPIView,self).post(request,format)

class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated,UpdateDeleteQuestionPermission]  # Only the owner or staff can edit/delete




class QuestionAndAnswerListCreate(generics.ListCreateAPIView):
    queryset = Answer.objects.select_related('question').all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user,question_id=self.kwargs.get("question_id"))


class QuestionAndAnswerRetriveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    queryset = Answer.objects.select_related('question').all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated,UpdateDeleteAnswerPermission]



class AnswerLikeDislikesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
        has_liked = request.data.get('has_liked')
        has_disliked = request.data.get('has_disliked')

        if has_liked and has_disliked:
            return Response(
                data={
                    "message": "You cannot like and dislike a question simultaneosly",
                    "code":"invalid_request"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            answer = Answer.objects.get(id=pk)
        except Answer.DoesNotExist:
            return Response(
                data={
                    "message": "No anwer to like or dislike",
                    "code": "invalid_anwer"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if has_liked:
            answer.no_of_likes = answer.no_of_likes + 1
            answer.save()
        if has_disliked:
            answer.no_of_dislikes = answer.no_of_dislikes + 1
            answer.save()
        return Response(
            data={
                "message":"Success"
            }
        )







class Login(APIView):

    authentication_classes = ()
    permission_classes = () 

    def post(self, request, format=None):
        data = request.data

        if not (data and data.get("username") and data.get("password")):
            return Response(
                data={
                    "code":"invalid_credentials",
                    "detail":"Username and Password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = data.get("username")
        user = ProgramUser.objects.filter(email__iexact=username).first()

        if not user:
            return Response(
                data={
                    "code":"invalid_user",
                    "detail":"User does not exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        password = data.get("password")

        if not user.check_password(password):
            return Response(
                data={
                    "code":"invalid_credentials",
                    "detail":"Incorrect Username or Password"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token,expires_in = get_jwt_token(user)
        
        return Response(data={"token":token,"expires_in":expires_in})
    
class Logout(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):
        token = request.headers.get("authorization")
        token = token.split("JWT ")[1]

        user_id = request.user.username

        cache_key = f"{user_id}:black_list_tokens"

        black_list_tokens = cache.get(cache_key) or []
        black_list_tokens.append(token)
        cache.set(cache_key,black_list_tokens,timeout=14400)
        return Response(data={"message":"Successfully Logged Out"})
    

class UserCreationAPIView(generics.CreateAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ProgramUserSerializer
    queryset = ProgramUser.objects.all()


    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code==201:
            id = response.data.get("id")
            user = ProgramUser.objects.get(id=id)
            token,_ = get_jwt_token(user)
            response.data['token'] = token
        return response



