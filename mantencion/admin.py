from django.contrib import admin
from .models import Vehicle, MaintenanceType, Maintenance, ServiceEvaluation, EvaluationChoice


class EvaluationChoiceInline(admin.TabularInline):
    model = EvaluationChoice
    extra = 3


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model', 'year', 'vehicle_type', 'owner_name', 'created_at')
    list_filter = ('vehicle_type', 'fuel_type', 'year', 'created_at')
    search_fields = ('license_plate', 'brand', 'model', 'owner_name', 'owner_phone')
    readonly_fields = ('created_at',)
    fieldsets = [
        ('Información del Vehículo', {
            'fields': ['license_plate', 'brand', 'model', 'year', 'vehicle_type', 'fuel_type', 'color']
        }),
        ('Información del Propietario', {
            'fields': ['owner_name', 'owner_phone', 'owner_email']
        }),
        ('Información del Sistema', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]


class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'estimated_duration', 'base_price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'scheduled_date', 'status', 'cost', 'created_at')
    list_filter = ('status', 'maintenance_type', 'scheduled_date', 'created_at')
    search_fields = ('vehicle__license_plate', 'vehicle__brand', 'vehicle__model', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = [
        ('Información Básica', {
            'fields': ['vehicle', 'maintenance_type', 'status']
        }),
        ('Fechas', {
            'fields': ['scheduled_date', 'start_date', 'completion_date']
        }),
        ('Detalles', {
            'fields': ['description', 'cost', 'notes']
        }),
        ('Información del Sistema', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


class ServiceEvaluationAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'maintenance', 'pub_date', 'is_active', 'was_published_recently')
    list_filter = ('pub_date', 'is_active')
    search_fields = ('question_text', 'maintenance__vehicle__license_plate')
    inlines = [EvaluationChoiceInline]
    fieldsets = [
        (None, {'fields': ['question_text', 'maintenance']}),
        ('Configuración', {'fields': ['pub_date', 'is_active']}),
    ]


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(MaintenanceType, MaintenanceTypeAdmin)
admin.site.register(Maintenance, MaintenanceAdmin)
admin.site.register(ServiceEvaluation, ServiceEvaluationAdmin)