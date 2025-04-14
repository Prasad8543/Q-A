from rest_framework import serializers
from django.contrib.auth import get_user_model

from .utils import generate_unique_username
from .models import ProgramUser, TimeStamp, AuditEnable, Question, Answer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
import uuid

# Get the User model (ProgramUser in this case)
User = get_user_model()

class ProgramUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, 
        allow_blank=True, 
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = ProgramUser
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'validators': [validate_password]},
        }

    def create(self, validated_data):
        # Auto-generate the username and handle user creation
        username = generate_unique_username()
        user = User.objects.create_user(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get('email'),
            password=validated_data['password'],
            username=username
        )
        return user


# TimeStamp Serializer
class TimeStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStamp
        fields = ['created_ts', 'updated_ts']


# AuditInfo Serializer
class AuditInfoSerializer(TimeStampSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    updated_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    attributes = serializers.JSONField(required=False)

    class Meta:
        model = AuditEnable
        fields = TimeStampSerializer.Meta.fields + ['created_by', 'updated_by', 'attributes']


# Question Serializer
class QuestionSerializer(AuditInfoSerializer):
    class Meta:
        model = Question
        fields = ["id",'question', 'no_of_answers'] + AuditInfoSerializer.Meta.fields 
        read_only_fields = ('id', "no_of_answers")

    def create(self, validated_data):
        question = Question.objects.create(
            **validated_data
        )
        return question


# Answer Serializer
class AnswerSerializer(AuditInfoSerializer):
    question = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields =['id', 'question','answer', 'no_of_likes','no_of_dislikes'] + AuditInfoSerializer.Meta.fields
        read_only_fields = ('no_of_likes','no_of_dislikes')

    def create(self, validated_data):
        answer = Answer.objects.create(
            **validated_data
        )
        return answer
    
    def get_question(self,answer):
        return answer.question.question
    
class QuestionWithAnswersSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question','no_of_answers', 'answers']