from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'surveys'

urlpatterns = [
    path('', views.SurveyListView.as_view(), name='survey_list'),
    path('<int:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
    path('<int:pk>/respond/', views.SurveyResponseView.as_view(), name='survey_response'),
    path('create/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('<int:pk>/edit/', views.SurveyUpdateView.as_view(), name='survey_edit'),
    path('<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey_delete'),
    path('<int:survey_pk>/results/', views.SurveyResultsView.as_view(), name='survey_results'),
    path('my-surveys/', views.UserSurveyListView.as_view(), name='user_survey_list'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

]
