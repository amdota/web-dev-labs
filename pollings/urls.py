from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from pollings import views
from pollings.views import UserViewSet

app_name = "pollings"

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'questions', views.QuestionViewSet, basename='questions')

questions_router = routers.NestedSimpleRouter(router, r'questions', lookup='question')
questions_router.register(r'answers', views.AnswerViewSet, basename='question-answers')

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users', UserViewSet.as_view(
        actions={'get': 'list', 'post': 'create'}), name='users-list'),
    path('users/<str:username>', UserViewSet.as_view(
        actions={'get': 'retrieve', 'head': 'exists', 'delete': 'destroy'}),
         name='users-detail'),
    path('', include(router.urls)),
    path('', include(questions_router.urls)),
]
