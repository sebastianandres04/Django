from django.contrib import admin
from django.utils.html import format_html
from django.template.response import TemplateResponse

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['choice_text', 'votes']
    readonly_fields = ['votes']


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently', 'total_votes_display', 'choices_count')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    date_hierarchy = 'pub_date'
    list_per_page = 25
    ordering = ['-pub_date']
    
    class Media:
        css = {
            'all': ('polls/admin.css',)
        }
    
    def total_votes_display(self, obj):
        """Muestra el total de votos con formato"""
        total = obj.total_votes()
        if total > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{}</span>',
                f"{total} voto{'s' if total != 1 else ''}"
            )
        return format_html('<span style="color: #6c757d;">Sin votos</span>')
    total_votes_display.short_description = 'Total de votos'
    total_votes_display.admin_order_field = 'choice__votes'
    
    def choices_count(self, obj):
        """Muestra el número de opciones disponibles"""
        count = obj.choice_set.count()
        return format_html(
            '<span style="color: #007bff;">{}</span>',
            f"{count} opción{'es' if count != 1 else ''}"
        )
    choices_count.short_description = 'Opciones'
    
    def get_queryset(self, request):
        """Optimiza las consultas para evitar N+1 queries"""
        return super().get_queryset(request).prefetch_related('choice_set')
    
    def changelist_view(self, request, extra_context=None):
        """Personaliza la vista de lista de cambios"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Gestión de Encuestas'
        extra_context['subtitle'] = 'Administra todas las encuestas del sistema'
        return super().changelist_view(request, extra_context)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'votes', 'percentage')
    list_filter = ['question__pub_date']
    search_fields = ['choice_text', 'question__question_text']
    list_per_page = 25
    ordering = ['-votes', 'choice_text']
    
    class Media:
        css = {
            'all': ('polls/admin.css',)
        }
    
    def percentage(self, obj):
        """Calcula y muestra el porcentaje de votos"""
        if obj.question.total_votes() > 0:
            percentage = (obj.votes / obj.question.total_votes()) * 100
            color = '#28a745' if percentage > 50 else '#ffc107' if percentage > 25 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, percentage
            )
        return format_html('<span style="color: #6c757d;">0%</span>')
    percentage.short_description = 'Porcentaje'
    percentage.admin_order_field = 'votes'
    
    def changelist_view(self, request, extra_context=None):
        """Personaliza la vista de lista de cambios"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Gestión de Opciones'
        extra_context['subtitle'] = 'Administra todas las opciones de respuesta'
        return super().changelist_view(request, extra_context)


# Registrar los modelos con sus respectivas configuraciones
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)

# Personalizar el título del sitio de administración
admin.site.site_header = "Administración del Sistema de Encuestas"
admin.site.site_title = "Encuestas Admin"
admin.site.index_title = "Panel de Administración"