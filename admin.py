from django.contrib import admin
from .models import Survey, Question, Choice, Response, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'survey', 'question_type', 'is_required', 'order')
    list_filter = ('survey', 'question_type')
    search_fields = ('text',)

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'text_answer', 'choice_answer')
    can_delete = False

class ResponseAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('survey', 'respondent', 'created_at')
    list_filter = ('survey', 'created_at')
    search_fields = ('survey__title', 'respondent__username')

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Response, ResponseAdmin)