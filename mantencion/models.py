from django.db import models
from django.utils import timezone
import datetime


class Vehicle(models.Model):
    """Modelo para representar vehículos"""
    VEHICLE_TYPES = [
        ('car', 'Automóvil'),
        ('truck', 'Camión'),
        ('motorcycle', 'Motocicleta'),
        ('bus', 'Autobús'),
        ('van', 'Van'),
    ]
    
    FUEL_TYPES = [
        ('gasoline', 'Gasolina'),
        ('diesel', 'Diésel'),
        ('electric', 'Eléctrico'),
        ('hybrid', 'Híbrido'),
        ('lpg', 'GLP'),
    ]
    
    license_plate = models.CharField(max_length=20, unique=True, verbose_name='Placa')
    brand = models.CharField(max_length=50, verbose_name='Marca')
    model = models.CharField(max_length=50, verbose_name='Modelo')
    year = models.IntegerField(verbose_name='Año')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, verbose_name='Tipo de Vehículo')
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, verbose_name='Tipo de Combustible')
    color = models.CharField(max_length=30, verbose_name='Color')
    owner_name = models.CharField(max_length=100, verbose_name='Nombre del Propietario')
    owner_phone = models.CharField(max_length=20, verbose_name='Teléfono')
    owner_email = models.EmailField(blank=True, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.model} - {self.license_plate}"
    
    def get_full_name(self):
        return f"{self.brand} {self.model} ({self.year})"


class MaintenanceType(models.Model):
    """Tipos de mantenimiento disponibles"""
    name = models.CharField(max_length=100, verbose_name='Nombre del Mantenimiento')
    description = models.TextField(verbose_name='Descripción')
    estimated_duration = models.DurationField(verbose_name='Duración Estimada')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Base')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Tipo de Mantenimiento'
        verbose_name_plural = 'Tipos de Mantenimiento'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Maintenance(models.Model):
    """Registro de mantenimientos realizados"""
    STATUS_CHOICES = [
        ('scheduled', 'Programado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='Vehículo')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, verbose_name='Tipo de Mantenimiento')
    scheduled_date = models.DateTimeField(verbose_name='Fecha Programada')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Inicio')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Finalización')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='Estado')
    description = models.TextField(blank=True, verbose_name='Descripción')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo')
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_type} ({self.get_status_display()})"
    
    def is_overdue(self):
        """Verifica si el mantenimiento está atrasado"""
        if self.status == 'scheduled' and timezone.now() > self.scheduled_date:
            return True
        return False
    
    def get_duration(self):
        """Calcula la duración del mantenimiento"""
        if self.start_date and self.completion_date:
            return self.completion_date - self.start_date
        return None


class ServiceEvaluation(models.Model):
    """Evaluaciones de servicios (adaptación de polls)"""
    maintenance = models.OneToOneField(Maintenance, on_delete=models.CASCADE, verbose_name='Mantenimiento')
    question_text = models.CharField(max_length=200, verbose_name='Pregunta de Evaluación')
    pub_date = models.DateTimeField('Fecha de Publicación', default=timezone.now)
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Evaluación de Servicio'
        verbose_name_plural = 'Evaluaciones de Servicios'
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def total_votes(self):
        """Calcula el total de votos para esta evaluación"""
        return sum(choice.votes for choice in self.choice_set.all())


class EvaluationChoice(models.Model):
    """Opciones de evaluación (adaptación de Choice)"""
    evaluation = models.ForeignKey(ServiceEvaluation, on_delete=models.CASCADE, verbose_name='Evaluación')
    choice_text = models.CharField(max_length=200, verbose_name='Opción de Evaluación')
    votes = models.IntegerField(default=0, verbose_name='Votos')
    
    class Meta:
        verbose_name = 'Opción de Evaluación'
        verbose_name_plural = 'Opciones de Evaluación'
    
    def __str__(self):
        return self.choice_text