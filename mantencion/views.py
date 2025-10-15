from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta

from .models import Vehicle, Maintenance, MaintenanceType, ServiceEvaluation, EvaluationChoice


class VehicleListView(generic.ListView):
    model = Vehicle
    template_name = 'mantecion/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Vehicle.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(license_plate__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(owner_name__icontains=search)
            )
        return queryset


class VehicleDetailView(generic.DetailView):
    model = Vehicle
    template_name = 'mantecion/vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        context['maintenances'] = Maintenance.objects.filter(vehicle=vehicle).order_by('-scheduled_date')
        context['upcoming_maintenances'] = Maintenance.objects.filter(
            vehicle=vehicle,
            status='scheduled',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:3]
        return context


class MaintenanceListView(generic.ListView):
    model = Maintenance
    template_name = 'mantecion/maintenance_list.html'
    context_object_name = 'maintenances'
    paginate_by = 15

    def get_queryset(self):
        queryset = Maintenance.objects.select_related('vehicle', 'maintenance_type').all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-scheduled_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Maintenance.STATUS_CHOICES
        context['overdue_count'] = Maintenance.objects.filter(
            status='scheduled',
            scheduled_date__lt=timezone.now()
        ).count()
        return context


class MaintenanceDetailView(generic.DetailView):
    model = Maintenance
    template_name = 'mantecion/maintenance_detail.html'
    context_object_name = 'maintenance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        maintenance = self.get_object()
        try:
            context['evaluation'] = ServiceEvaluation.objects.get(maintenance=maintenance)
        except ServiceEvaluation.DoesNotExist:
            context['evaluation'] = None
        return context


class ServiceEvaluationListView(generic.ListView):
    model = ServiceEvaluation
    template_name = 'mantecion/evaluation_list.html'
    context_object_name = 'evaluations'

    def get_queryset(self):
        return ServiceEvaluation.objects.filter(
            is_active=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:10]


class ServiceEvaluationDetailView(generic.DetailView):
    model = ServiceEvaluation
    template_name = 'mantecion/evaluation_detail.html'
    context_object_name = 'evaluation'

    def get_queryset(self):
        return ServiceEvaluation.objects.filter(
            is_active=True,
            pub_date__lte=timezone.now()
        )


class ServiceEvaluationResultsView(generic.DetailView):
    model = ServiceEvaluation
    template_name = 'mantecion/evaluation_results.html'
    context_object_name = 'evaluation'

    def get_queryset(self):
        return ServiceEvaluation.objects.filter(
            is_active=True,
            pub_date__lte=timezone.now()
        )


def vote_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(ServiceEvaluation, pk=evaluation_id)
    try:
        selected_choice = evaluation.evaluationchoice_set.get(pk=request.POST['choice'])
    except (KeyError, EvaluationChoice.DoesNotExist):
        return render(request, 'mantecion/evaluation_detail.html', {
            'evaluation': evaluation,
            'error_message': "No seleccionaste una opción.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('mantecion:evaluation_results', args=(evaluation.id,)))


def dashboard(request):
    """Vista del dashboard principal"""
    context = {
        'total_vehicles': Vehicle.objects.count(),
        'total_maintenances': Maintenance.objects.count(),
        'pending_maintenances': Maintenance.objects.filter(status='scheduled').count(),
        'overdue_maintenances': Maintenance.objects.filter(
            status='scheduled',
            scheduled_date__lt=timezone.now()
        ).count(),
        'recent_maintenances': Maintenance.objects.filter(
            completion_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'upcoming_maintenances': Maintenance.objects.filter(
            status='scheduled',
            scheduled_date__gte=timezone.now(),
            scheduled_date__lte=timezone.now() + timedelta(days=7)
        ).order_by('scheduled_date')[:5],
        'recent_vehicles': Vehicle.objects.order_by('-created_at')[:5],
    }
    return render(request, 'mantecion/dashboard.html', context)