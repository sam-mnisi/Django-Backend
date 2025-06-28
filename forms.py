from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Question, Choice

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'is_required', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'value']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Display text'}),
            'value': forms.TextInput(attrs={'placeholder': 'Value'}),
        }

# Formset for questions
QuestionFormSet = inlineformset_factory(
    Survey, Question, 
    form=QuestionForm, 
    extra=1, 
    can_delete=True
)

# Formset for choices (used in admin)
ChoiceFormSet = inlineformset_factory(
    Question, Choice,
    form=ChoiceForm,
    extra=2,
    can_delete=True
)