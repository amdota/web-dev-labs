from django.contrib.auth.models import User
from django.http import Http404
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, inline_serializer, OpenApiExample
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from pollings.models import Question, Answer
from pollings.permissions import UserViewPermission, IsOwnerOrAdmin
from pollings.serializers import UserSerializer, QuestionSerializer, AnswerSerializer


def is_already_vote(question, user_id):
    for answer in question.answers.all():
        result_set = answer.voters.filter(pk=user_id)
        if result_set.count() != 0:
            return True
    return False


def you_have_already_vote_response():
    return Response({'message': 'You have already vote on this question'},
                    status=status.HTTP_403_FORBIDDEN)


@extend_schema_view(
    list=extend_schema(
        summary="Get list of users",
        description="Only stuff can see all users",
        tags=["User"]
    ),
    retrieve=extend_schema(
        summary="Get user",
        tags=["User"]
    ),
    destroy=extend_schema(
        summary="Delete user",
        tags=["User"]
    ),
    create=extend_schema(
        summary="Register user",
        tags=["User"]
    ),
    exists=extend_schema(
        summary="Check user existence",
        methods=["HEAD"],
        tags=["User"]
    )
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserViewPermission]
    lookup_field = "username"

    def exists(self, request, *args, **kwargs):
        try:
            _ret = self.retrieve(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        except Http404 as e:
            return Response(status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(
        summary="Get list of questions",
        tags=["Question"]
    ),
    retrieve=extend_schema(
        summary="Get question",
        tags=["Question"]
    ),
    destroy=extend_schema(
        summary="Delete question",
        tags=["Question"]
    ),
    create=extend_schema(
        summary="Create question",
        tags=["Question"]
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        exclude=True
    )
)
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    @extend_schema(tags=["Question"],
                   summary="Check whether you have already vote",
                   responses={200: inline_serializer(
                       name="IsAlreadyVoteAnswer",
                       fields={
                           'is-already-vote': serializers.BooleanField()
                       }
                   )})
    @action(detail=True, url_path='is-already-vote', permission_classes=[IsAuthenticated])
    def is_already_vote(self, request, pk=None):
        """Check if the current user vote on question=id"""
        question = self.get_object()
        if is_already_vote(question, request.user.id):
            return Response({'is-already-vote': True})
        return Response({'is-already-vote': False})


voteAnswerSerializer = inline_serializer(
                       name="VoteAnswer",
                       fields={
                           'message': serializers.CharField()
                       })


@extend_schema_view(
    list=extend_schema(
        exclude=True
    ),
    retrieve=extend_schema(
        summary="Get answer",
        tags=["Answer"]
    )
)
class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(tags=["Answer"],
                   summary="Vote for answer",
                   request=None,
                   responses={200: voteAnswerSerializer, 403: voteAnswerSerializer}
                   ,
                   examples=[
                       OpenApiExample(
                           'Successful vote',
                           value={'message': 'Thank you for your vote'}
                       ),
                       OpenApiExample(
                           'You can\'t vote',
                           value={'message': 'You have already vote on this question'}
                           , status_codes=["403"]
                       )
                   ]
                   )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def vote(self, request, question_pk=None, pk=None):
        """
        Votes for answer=id in question=question_pk
        """
        answer = self.get_object()
        question = Question.objects.get(pk=question_pk)
        if is_already_vote(question, request.user.id):
            return you_have_already_vote_response()
        answer.voters.add(request.user.id)
        answer.save()
        return Response({'message': 'Thank you for your vote'})
