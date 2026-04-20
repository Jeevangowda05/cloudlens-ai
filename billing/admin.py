from django.contrib import admin
from api.models import BillingCache, CostAlert


@admin.register(BillingCache)
class BillingCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'cloud_provider', 'total_cost', 'is_fresh', 'fetched_at', 'expires_at')
    list_filter = ('cloud_provider', 'is_fresh')
    search_fields = ('user__username', 'user__email')


@admin.register(CostAlert)
class CostAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'cloud_provider', 'alert_type', 'status', 'triggered_at')
    list_filter = ('cloud_provider', 'alert_type', 'status')
    search_fields = ('title', 'description', 'user__username', 'user__email')
