from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count

from .models import Survey, Question, Choice, Response, Answer
from .forms import SurveyForm, QuestionFormSet

class SurveyListView(ListView):
    model = Survey
    template_name = 'surveys/survey_list.html'
    context_object_name = 'surveys'
    
    def get_queryset(self):
        return Survey.objects.filter(is_active=True)

# def survey_list_view(request):
#     active_surveys = Survey.objects.filter(is_active=True)
#     context = {'surveys': active_surveys}
#     return render(request, 'surveys/survey_list.html', context)

class UserSurveyListView(LoginRequiredMixin, ListView):
    model = Survey
    template_name = 'surveys/user_survey_list.html'
    context_object_name = 'surveys'
    
    def get_queryset(self):
        return Survey.objects.filter(created_by=self.request.user)

class SurveyDetailView(DetailView):
    model = Survey
    template_name = 'surveys/survey_detail.html'
    context_object_name = 'survey'

class SurveyCreateView(LoginRequiredMixin, CreateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['question_formset'] = QuestionFormSet(self.request.POST)
        else:
            context['question_formset'] = QuestionFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        question_formset = context['question_formset']
        
        if question_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()
            
            question_formset.instance = self.object
            question_formset.save()
            
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['question_formset'] = QuestionFormSet(self.request.POST, instance=self.object)
        else:
            context['question_formset'] = QuestionFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        question_formset = context['question_formset']
        
        if question_formset.is_valid():
            self.object = form.save()
            question_formset.instance = self.object
            question_formset.save()
            
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SurveyDeleteView(LoginRequiredMixin, DeleteView):
    model = Survey
    template_name = 'surveys/survey_confirm_delete.html'
    success_url = reverse_lazy('surveys:user_survey_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

class SurveyResponseView(CreateView):
    model = Response
    fields = []
    template_name = 'surveys/survey_response.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.survey
        return context
    
    def form_valid(self, form):
        response = form.save(commit=False)
        response.survey = self.survey
        if self.request.user.is_authenticated:
            response.respondent = self.request.user
        response.save()
        
        for question in self.survey.questions.all():
            answer_text = self.request.POST.get(f'question_{question.id}')
            choice_ids = self.request.POST.getlist(f'question_{question.id}_choices')
            
            answer = Answer(
                response=response,
                question=question
            )
            
            if question.question_type == 'text':
                answer.text_answer = answer_text
            else:
                answer.save()
                choices = Choice.objects.filter(id__in=choice_ids)
                answer.choice_answer.set(choices)
            
            answer.save()
        
        messages.success(self.request, 'Thank you for completing the survey!')
        return redirect('surveys:survey_list')

class SurveyResultsView(LoginRequiredMixin, DetailView):
    model = Survey
    template_name = 'surveys/survey_results.html'
    context_object_name = 'survey'
    
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get response count
        context['response_count'] = self.object.responses.count()
        
        # Prepare question statistics
        question_stats = []
        
        for question in self.object.questions.all():
            stats = {
                'question': question,
                'answer_count': Answer.objects.filter(
                    response__survey=self.object,
                    question=question
                ).count()
            }
            
            if question.question_type == 'text':
                stats['type'] = 'text'
                stats['answers'] = Answer.objects.filter(
                    response__survey=self.object,
                    question=question
                ).exclude(text_answer__exact='').values_list('text_answer', flat=True)
            else:
                stats['type'] = 'choice'
                stats['choices'] = []
                
                for choice in question.choices.all():
                    choice_count = Answer.objects.filter(
                        response__survey=self.object,
                        question=question,
                        choice_answer=choice
                    ).count()
                    
                    stats['choices'].append({
                        'choice': choice,
                        'count': choice_count,
                        'percentage': (choice_count / stats['answer_count'] * 100) if stats['answer_count'] > 0 else 0
                    })
            
            question_stats.append(stats)
        
        context['question_stats'] = question_stats
        
        return context
