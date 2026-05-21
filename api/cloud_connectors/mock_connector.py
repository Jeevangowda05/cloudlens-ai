"""
Mock Cloud Connectors for Demo Mode
Returns realistic pre-generated billing data so the project can be demonstrated
without real AWS/Azure/GCP credentials.
"""

from datetime import datetime, timedelta
from random import Random


class MockCloudConnector:
    """Base class for mock cloud provider connectors."""

    def __init__(self, provider: str, seed: int = 42):
        self.provider = provider
        self.random = Random(seed)
        self.demo_account_id = 'demo-account-12345'

    def connect(self, credentials: dict) -> dict:
        """Mock connection always succeeds."""
        return {
            'success': True,
            'account_id': self.demo_account_id,
            'provider': self.provider,
            'message': f'Connected to demo {self.provider} account',
            'is_mock': True,
        }

    def get_billing_data(self, days: int = 30) -> dict:
        """Generate deterministic, realistic billing data."""
        daily_records = []
        base_cost = self._base_daily_cost()

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).date()
            weekly_factor = 1 + ((i % 7) * 0.03)
            noise = self.random.uniform(-0.08, 0.12)
            total_cost = round(base_cost * weekly_factor * (1 + noise), 2)

            service_costs = self._service_costs(total_cost)
            region_costs = self._region_costs(total_cost)

            daily_records.append({
                'date': str(date),
                'total_cost': total_cost,
                'service_costs': service_costs,
                'region_costs': region_costs,
            })

        total = round(sum(item['total_cost'] for item in daily_records), 2)

        return {
            'provider': self.provider,
            'account_id': self.demo_account_id,
            'period': {
                'start_date': str((datetime.now() - timedelta(days=days)).date()),
                'end_date': str(datetime.now().date()),
            },
            'summary': {
                'total_cost': total,
                'daily_average': round(total / days, 2),
                'daily_records': daily_records,
            },
            'is_mock': True,
        }

    def _base_daily_cost(self) -> float:
        return 500.0

    def _service_costs(self, total_cost: float) -> dict:
        return {
            'EC2': round(total_cost * 0.46, 2),
            'RDS': round(total_cost * 0.20, 2),
            'S3': round(total_cost * 0.16, 2),
            'Network': round(total_cost * 0.10, 2),
            'Other': round(total_cost * 0.08, 2),
        }

    def _region_costs(self, total_cost: float) -> dict:
        return {
            'us-east-1': round(total_cost * 0.50, 2),
            'us-west-2': round(total_cost * 0.30, 2),
            'eu-west-1': round(total_cost * 0.20, 2),
        }


class MockAWSConnector(MockCloudConnector):
    def __init__(self):
        super().__init__('AWS')


class MockAzureConnector(MockCloudConnector):
    def __init__(self):
        super().__init__('AZURE')

    def _base_daily_cost(self) -> float:
        return 420.0


class MockGCPConnector(MockCloudConnector):
    def __init__(self):
        super().__init__('GCP')

    def _base_daily_cost(self) -> float:
        return 380.0
