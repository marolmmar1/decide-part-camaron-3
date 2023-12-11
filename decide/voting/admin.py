from django.contrib import admin
from django.utils import timezone

from .models import QuestionOption
from .models import Question
from .models import Voting

from .filters import StartedFilter

def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)

def single_choice(modeladmin, request, queryset):
    queryset.update(voting_type='S')

def multiple_choice(modeladmin, request, queryset):
    queryset.update(voting_type='M')

def hierarchy(modeladmin, request, queryset):
    queryset.update(voting_type='H')


def many_questions(modeladmin, request, queryset):
    queryset.update(voting_type='Q')


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]

admin.site.register(Question, QuestionAdmin)

class VotingTypeFilter(admin.SimpleListFilter):
    title = 'voting type'
    parameter_name = 'voting_type'

    def lookups(self, request, model_admin):
        return [
            ('S', 'Single Choice'),
            ('M', 'Multiple Choice'),
            ('H', 'Hierarchy'),
            ('Q', 'Many Questions'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(voting_type=self.value())

class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'postproc_type', 'voting_type')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter, VotingTypeFilter)
    search_fields = ('name', )

    actions = [start, stop, tally]

admin.site.register(Voting, VotingAdmin)
