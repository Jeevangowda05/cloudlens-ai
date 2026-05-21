from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from api.models import CloudCredentials, BillingCache, DailyBillingRecord, Recommendation, CostAlert
from api.cloud_connectors import ConnectorFactory


class Command(BaseCommand):
    help = 'Seed demo cloud data for presentations and local testing'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='demo@cloudlens.ai',
            defaults={
                'email': 'demo@cloudlens.ai',
                'first_name': 'Demo',
                'last_name': 'User',
            },
        )
        if created:
            user.set_password('demo123456')
            user.save()

        self.stdout.write(self.style.SUCCESS(f'Using demo user: {user.username}'))

        providers = ['AWS', 'AZURE', 'GCP']
        for provider in providers:
            connector = ConnectorFactory.get_connector(provider)
            billing_data = connector.get_billing_data(days=30)
            summary = billing_data['summary']
            daily_records = summary['daily_records']

            CloudCredentials.objects.update_or_create(
                user=user,
                cloud_provider=provider,
                defaults={
                    'encrypted_key_1': 'demo-key-1',
                    'encrypted_key_2': 'demo-key-2',
                    'encrypted_key_3': 'demo-key-3',
                    'additional_data': {
                        'is_mock': True,
                        'demo_mode': True,
                        'sample_provider': provider,
                        'demo_label': 'Demo tenant – using sample cloud billing data',
                    },
                    'is_active': True,
                    'is_verified': True,
                    'connection_error': '',
                },
            )

            cache_expires = timezone.now() + timedelta(hours=12)
            BillingCache.objects.update_or_create(
                user=user,
                cloud_provider=provider,
                defaults={
                    'total_cost': summary['total_cost'],
                    'daily_costs': daily_records,
                    'service_costs': daily_records[-1]['service_costs'] if daily_records else {},
                    'anomalies': [],
                    'expires_at': cache_expires,
                    'is_fresh': True,
                },
            )

            for record in daily_records:
                DailyBillingRecord.objects.update_or_create(
                    user=user,
                    cloud_provider=provider,
                    date=record['date'],
                    defaults={
                        'total_cost': record['total_cost'],
                        'service_costs': record['service_costs'],
                        'region_costs': record['region_costs'],
                        'is_anomaly': False,
                        'anomaly_score': 0,
                        'raw_data': record,
                    },
                )

            Recommendation.objects.update_or_create(
                user=user,
                cloud_provider=provider,
                title=f'{provider} Rightsize Idle Resources',
                defaults={
                    'description': 'Several compute resources appear underutilized in the demo dataset.',
                    'action': 'Review idle compute instances and reduce oversized workloads.',
                    'reason': 'Low utilization detected across the sample billing history.',
                    'estimated_monthly_savings': 124.50,
                    'estimated_yearly_savings': 1494.00,
                    'priority_score': 10,
                    'is_active': True,
                    'is_completed': False,
                },
            )

            CostAlert.objects.update_or_create(
                user=user,
                alert_type='FORECAST',
                cloud_provider=provider,
                title=f'{provider} forecast indicates increased spend',
                defaults={
                    'description': 'Demo forecast projects higher spend over the next 30 days.',
                    'cost_amount': summary['total_cost'],
                    'cost_change_percent': 18.7,
                    'status': 'TRIGGERED',
                    'is_sent': False,
                },
            )

            self.stdout.write(self.style.SUCCESS(f'Seeded demo data for {provider}'))

        self.stdout.write(self.style.SUCCESS('Demo data seeding completed successfully.'))
