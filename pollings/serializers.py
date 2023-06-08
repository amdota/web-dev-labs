import datetime
from abc import ABC

from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from pollings.models import Question, Answer


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'password', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnswerSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_votes(self, obj):
        return obj.voters.count()

    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'votes']
        read_only_fields = ['id', 'votes']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    author_username = serializers.StringRelatedField(source='author')

    class Meta:
        model = Question
        fields = ['id', 'author', 'author_username', 'question_text', 'pub_date', 'answers']
        read_only_fields = ['id', 'pub_date']

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        question = Question.objects.create(author=validated_data["author"],
                                           question_text=validated_data['question_text'],
                                           pub_date=datetime.datetime.now())
        for answer in answers:
            Answer.objects.create(question=question, answer_text=answer["answer_text"])
        return question
