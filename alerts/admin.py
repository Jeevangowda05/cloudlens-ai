from django.contrib import admin
from .models import AlertRule, AlertLog


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'alert_type', 'cloud_provider', 'threshold_value', 'is_active')
    list_filter = ('alert_type', 'cloud_provider', 'is_active')
    search_fields = ('name', 'user__username', 'user__email')


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'alert_type', 'cloud_provider', 'status', 'triggered_at')
    list_filter = ('alert_type', 'cloud_provider', 'status')
    search_fields = ('title', 'description', 'user__username', 'user__email')
