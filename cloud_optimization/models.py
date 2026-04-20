from django.contrib.auth.models import User
from django.db import models


class CostSimulation(models.Model):
    """What-If Simulator scenarios."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cost_simulations')
    name = models.CharField(max_length=200)
    base_monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    rightsizing_percent = models.IntegerField(default=10)
    reserved_savings_percent = models.IntegerField(default=18)
    spot_instances_percent = models.IntegerField(default=0)
    projected_monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_savings = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_savings = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class RegionOptimization(models.Model):
    """Region recommendation data."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='region_optimizations')
    current_region = models.CharField(max_length=50)
    recommended_region = models.CharField(max_length=50)
    current_monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    potential_monthly_savings = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_profile_current = models.CharField(max_length=20)
    carbon_profile_recommended = models.CharField(max_length=20)
    latency_impact = models.CharField(max_length=20, default='low')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-potential_monthly_savings']


class IdleResource(models.Model):
    """Idle resources detection."""

    RESOURCE_TYPES = [
        ('EC2', 'EC2 Instance'),
        ('RDS', 'RDS Database'),
        ('STORAGE', 'Storage'),
        ('NAT', 'NAT Gateway'),
        ('ELB', 'Load Balancer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='idle_resources')
    cloud_provider = models.CharField(max_length=20)
    resource_id = models.CharField(max_length=200)
    resource_name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    idle_duration_days = models.IntegerField()
    cpu_percent = models.DecimalField(max_digits=5, decimal_places=2)
    network_mbph = models.DecimalField(max_digits=8, decimal_places=2)
    last_accessed = models.DateTimeField()
    detected_at = models.DateTimeField(auto_now_add=True)
    recommended_action = models.TextField()

    class Meta:
        ordering = ['-monthly_cost']


class CostReport(models.Model):
    """Generated cost reports."""

    REPORT_TYPES = [
        ('MONTHLY', 'Monthly Summary'),
        ('EXECUTIVE', 'Executive Summary'),
        ('DETAILED', 'Detailed Analysis'),
        ('CUSTOM', 'Custom Report'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cost_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    service_breakdown = models.JSONField(default=dict)
    region_breakdown = models.JSONField(default=dict)
    tag_breakdown = models.JSONField(default=dict)
    recommendations_count = models.IntegerField(default=0)
    anomalies_detected = models.IntegerField(default=0)
    file_format = models.CharField(max_length=10, default='pdf')
    file_path = models.CharField(max_length=300, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    sent_to_emails = models.TextField(blank=True)

    class Meta:
        ordering = ['-generated_at']


class TagCostGroup(models.Model):
    """Tag-based cost allocation."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tag_cost_groups')
    cloud_provider = models.CharField(max_length=20)
    tag_key = models.CharField(max_length=200)
    tag_value = models.CharField(max_length=200)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    resource_count = models.IntegerField()
    services = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_cost']
        unique_together = ('user', 'cloud_provider', 'tag_key', 'tag_value')
