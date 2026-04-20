from django.contrib import admin
from api.models import DailyBillingRecord, Recommendation


@admin.register(DailyBillingRecord)
class DailyBillingRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'cloud_provider', 'date', 'total_cost', 'is_anomaly')
    list_filter = ('cloud_provider', 'is_anomaly', 'date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'cloud_provider',
        'estimated_monthly_savings',
        'priority_score',
        'is_active',
        'is_completed',
    )
    list_filter = ('cloud_provider', 'is_active', 'is_completed', 'priority_score')
    search_fields = ('title', 'description', 'user__username', 'user__email')
