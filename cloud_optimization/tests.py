from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import DailyBillingRecord, Recommendation
from .models import IdleResource, TagCostGroup


class CloudOptimizationApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='optimizer@example.com',
            email='optimizer@example.com',
            password='StrongPass123!',
        )
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_simulation_can_be_created(self):
        response = self.client.post(
            '/api/optimize/simulate/',
            {
                'name': 'Test scenario',
                'base_monthly_cost': '1000.00',
                'rightsizing_percent': 10,
                'reserved_savings_percent': 20,
                'spot_instances_percent': 5,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('simulation', response.data)
        self.assertEqual(response.data['simulation']['name'], 'Test scenario')

    def test_region_advisor_returns_recommendations(self):
        response = self.client.get('/api/optimize/regions/?provider=AWS&current_region=us-east-1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)

    def test_simulation_rejects_invalid_percentages(self):
        response = self.client.post(
            '/api/optimize/simulate/',
            {'base_monthly_cost': '1000.00', 'rightsizing_percent': 120},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_idle_resources_returns_totals(self):
        IdleResource.objects.create(
            user=self.user,
            cloud_provider='AWS',
            resource_id='i-123456',
            resource_name='test-instance',
            resource_type='EC2',
            monthly_cost=Decimal('42.50'),
            idle_duration_days=14,
            cpu_percent=Decimal('1.25'),
            network_mbph=Decimal('0.15'),
            last_accessed=timezone.now(),
            recommended_action='Stop or terminate instance',
        )

        response = self.client.get('/api/optimize/idle-resources/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['total_potential_savings'], 42.5)

    def test_report_generation_uses_billing_data(self):
        DailyBillingRecord.objects.create(
            user=self.user,
            cloud_provider='AWS',
            date=timezone.now().date(),
            total_cost=Decimal('100.00'),
            service_costs={'EC2': 60, 'S3': 40},
            region_costs={'us-east-1': 100},
        )
        Recommendation.objects.create(
            user=self.user,
            cloud_provider='AWS',
            title='Rightsize EC2',
            description='Downsize underutilized instances',
            action='Apply resize',
            reason='Low CPU usage',
            estimated_monthly_savings=Decimal('20.00'),
            estimated_yearly_savings=Decimal('240.00'),
            priority_score=5,
            is_active=True,
        )

        today = timezone.now().date().isoformat()
        response = self.client.post(
            '/api/optimize/reports/',
            {'period_start': today, 'period_end': today, 'report_type': 'MONTHLY'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['report']['total_cost'], 100.0)

    def test_tag_allocation_lists_provider_filtered_groups(self):
        TagCostGroup.objects.create(
            user=self.user,
            cloud_provider='AWS',
            tag_key='environment',
            tag_value='prod',
            total_cost=Decimal('120.00'),
            monthly_cost=Decimal('120.00'),
            resource_count=3,
            services={'EC2': {'count': 2, 'cost': 100}},
        )
        TagCostGroup.objects.create(
            user=self.user,
            cloud_provider='AZURE',
            tag_key='environment',
            tag_value='dev',
            total_cost=Decimal('90.00'),
            monthly_cost=Decimal('90.00'),
            resource_count=2,
            services={'VM': {'count': 2, 'cost': 90}},
        )

        response = self.client.get('/api/optimize/tags/?provider=AWS')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['total_cost'], 120.0)
