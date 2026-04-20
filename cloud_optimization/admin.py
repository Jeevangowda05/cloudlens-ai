from django.contrib import admin

from .models import CostReport, CostSimulation, IdleResource, RegionOptimization, TagCostGroup


@admin.register(CostSimulation)
class CostSimulationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'base_monthly_cost', 'projected_monthly_cost', 'monthly_savings', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'name')


@admin.register(RegionOptimization)
class RegionOptimizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_region', 'recommended_region', 'potential_monthly_savings')
    list_filter = ('current_region', 'recommended_region')
    search_fields = ('user__username',)


@admin.register(IdleResource)
class IdleResourceAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource_name', 'resource_type', 'cloud_provider', 'monthly_cost', 'idle_duration_days')
    list_filter = ('resource_type', 'cloud_provider', 'detected_at')
    search_fields = ('user__username', 'resource_name')


@admin.register(CostReport)
class CostReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_type', 'title', 'total_cost', 'period_start', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('user__username', 'title')


@admin.register(TagCostGroup)
class TagCostGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag_key', 'tag_value', 'total_cost', 'monthly_cost')
    list_filter = ('cloud_provider', 'tag_key')
    search_fields = ('user__username', 'tag_key', 'tag_value')
