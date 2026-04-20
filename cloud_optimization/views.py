from datetime import date
from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import DailyBillingRecord, Recommendation
from .models import CostReport, CostSimulation, IdleResource, TagCostGroup


class CostSimulationView(APIView):
    """Create and manage cost simulations."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            base_cost = Decimal(str(request.data.get('base_monthly_cost', 0)))
            rightsizing = int(request.data.get('rightsizing_percent', 10))
            reserved = int(request.data.get('reserved_savings_percent', 18))
            spot = int(request.data.get('spot_instances_percent', 0))
            if base_cost < 0:
                return Response({'error': 'base_monthly_cost must be non-negative'}, status=status.HTTP_400_BAD_REQUEST)
            if any(percent < 0 or percent > 100 for percent in [rightsizing, reserved, spot]):
                return Response(
                    {'error': 'Percentage values must be between 0 and 100'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rightsized_cost = base_cost * (1 - Decimal(rightsizing) / 100)
            after_reserved = rightsized_cost * (1 - Decimal(reserved) / 100)
            final_cost = after_reserved * (1 - Decimal(spot) / 100)

            monthly_savings = base_cost - final_cost
            yearly_savings = monthly_savings * 12

            simulation = CostSimulation.objects.create(
                user=request.user,
                name=request.data.get('name', 'Simulation'),
                base_monthly_cost=base_cost,
                rightsizing_percent=rightsizing,
                reserved_savings_percent=reserved,
                spot_instances_percent=spot,
                projected_monthly_cost=final_cost,
                monthly_savings=monthly_savings,
                yearly_savings=yearly_savings,
            )

            return Response(
                {
                    'simulation': {
                        'id': simulation.id,
                        'name': simulation.name,
                        'base_cost': float(base_cost),
                        'projected_cost': float(final_cost),
                        'monthly_savings': float(monthly_savings),
                        'yearly_savings': float(yearly_savings),
                    }
                },
                status=status.HTTP_201_CREATED,
            )

        except (ValueError, ArithmeticError):
            return Response({'error': 'Invalid simulation input'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Unable to create simulation'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        simulations = CostSimulation.objects.filter(user=request.user)
        data = [
            {
                'id': simulation.id,
                'name': simulation.name,
                'base_cost': float(simulation.base_monthly_cost),
                'projected_cost': float(simulation.projected_monthly_cost),
                'monthly_savings': float(simulation.monthly_savings),
                'yearly_savings': float(simulation.yearly_savings),
                'created_at': simulation.created_at,
            }
            for simulation in simulations
        ]

        return Response({'simulations': data})


class RegionAdvisorView(APIView):
    """Region optimization recommendations."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            current_region = request.query_params.get('current_region', 'us-east-1')

            regions = {
                'us-east-1': 420,
                'us-west-2': 395,
                'eu-west-1': 438,
                'ap-south-1': 465,
                'eu-north-1': 384,
            }
            carbon_profiles = {
                'us-east-1': 'Medium',
                'us-west-2': 'Low',
                'eu-west-1': 'Medium',
                'ap-south-1': 'High',
                'eu-north-1': 'Low',
            }

            current_cost = Decimal(str(regions.get(current_region, 420)))
            recommendations = []

            for region, cost in regions.items():
                if region == current_region:
                    continue

                savings = current_cost - Decimal(str(cost))
                if savings > 0:
                    recommendations.append(
                        {
                            'code': region,
                            'name': f'Region {region}',
                            'monthly_cost': cost,
                            'potential_savings': float(savings),
                            'carbon_profile': carbon_profiles.get(region, 'Medium'),
                        }
                    )

            recommendations.sort(key=lambda rec: rec['potential_savings'], reverse=True)

            return Response(
                {
                    'current_region': current_region,
                    'current_cost': float(current_cost),
                    'recommendations': recommendations[:3],
                }
            )

        except Exception:
            return Response({'error': 'Unable to fetch region recommendations'}, status=status.HTTP_400_BAD_REQUEST)


class IdleResourcesView(APIView):
    """Detect and manage idle resources."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            idle_resources = IdleResource.objects.filter(user=request.user)
            data = [
                {
                    'id': resource.id,
                    'name': resource.resource_name,
                    'type': resource.resource_type,
                    'provider': resource.cloud_provider,
                    'monthly_cost': float(resource.monthly_cost),
                    'idle_duration_days': resource.idle_duration_days,
                    'cpu_percent': float(resource.cpu_percent),
                    'network_mbph': float(resource.network_mbph),
                    'recommendation': resource.recommended_action,
                }
                for resource in idle_resources
            ]

            total_savings = sum(float(resource.monthly_cost) for resource in idle_resources)
            return Response(
                {
                    'resources': data,
                    'count': len(data),
                    'total_potential_savings': total_savings,
                }
            )

        except Exception:
            return Response({'error': 'Unable to list idle resources'}, status=status.HTTP_400_BAD_REQUEST)


class CostReportView(APIView):
    """Generate and manage cost reports."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            period_start = date.fromisoformat(str(request.data.get('period_start')))
            period_end = date.fromisoformat(str(request.data.get('period_end')))
            report_type = request.data.get('report_type', 'MONTHLY')

            records = DailyBillingRecord.objects.filter(
                user=request.user,
                date__range=[period_start, period_end],
            )

            total_cost = sum(float(record.total_cost) for record in records)
            service_breakdown = {}
            for record in records:
                for service, cost in (record.service_costs or {}).items():
                    service_breakdown[service] = service_breakdown.get(service, 0) + cost

            recommendations_count = Recommendation.objects.filter(
                user=request.user,
                is_active=True,
            ).count()

            report = CostReport.objects.create(
                user=request.user,
                report_type=report_type,
                title=f'{report_type} Report {period_start}',
                period_start=period_start,
                period_end=period_end,
                total_cost=Decimal(str(total_cost)),
                service_breakdown=service_breakdown,
                recommendations_count=recommendations_count,
            )

            return Response(
                {
                    'report': {
                        'id': report.id,
                        'type': report.report_type,
                        'total_cost': float(report.total_cost),
                        'generated_at': report.generated_at,
                    }
                },
                status=status.HTTP_201_CREATED,
            )

        except (TypeError, ValueError):
            return Response({'error': 'Invalid report input'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Unable to generate report'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        reports = CostReport.objects.filter(user=request.user)
        data = [
            {
                'id': report.id,
                'type': report.report_type,
                'title': report.title,
                'total_cost': float(report.total_cost),
                'period': f'{report.period_start} to {report.period_end}',
                'generated_at': report.generated_at,
            }
            for report in reports
        ]

        return Response({'reports': data})


class TagCostAllocationView(APIView):
    """Tag-based cost allocation and tracking."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider = request.query_params.get('provider', 'AWS')
            tag_groups = TagCostGroup.objects.filter(user=request.user, cloud_provider=provider)

            data = [
                {
                    'id': tag_group.id,
                    'tag_key': tag_group.tag_key,
                    'tag_value': tag_group.tag_value,
                    'total_cost': float(tag_group.total_cost),
                    'monthly_cost': float(tag_group.monthly_cost),
                    'resource_count': tag_group.resource_count,
                    'services': tag_group.services,
                }
                for tag_group in tag_groups
            ]

            total = sum(float(tag_group.total_cost) for tag_group in tag_groups)
            return Response({'tag_groups': data, 'total_cost': total, 'count': len(data)})

        except Exception:
            return Response({'error': 'Unable to fetch tag allocation'}, status=status.HTTP_400_BAD_REQUEST)
