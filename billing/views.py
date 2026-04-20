from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.conf import settings

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_billing_ai(request):
    """
    Chat with AI about your cloud billing (FREE via OpenRouter).
    """
    try:
        user_message = request.data.get('message', '')
        if not user_message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        
        # Get user's latest billing data for context
        billing_context = []
        try:
            from api.models import CloudConnection, BillingData
            
            connections = CloudConnection.objects.filter(user=user, is_active=True)
            
            for conn in connections:
                try:
                    latest_billing = BillingData.objects.filter(
                        cloud_connection=conn
                    ).order_by('-date')[:30]
                    
                    total_cost = sum(float(b.total_cost) for b in latest_billing)
                    daily_avg = total_cost / 30 if latest_billing.exists() else 0
                    
                    billing_context.append({
                        'provider': conn.get_cloud_provider_display(),
                        'total_cost_30days': round(total_cost, 2),
                        'daily_average': round(daily_avg, 2),
                        'services': list(set(
                            str(b.service_name) for b in latest_billing if b.service_name
                        )[:5])
                    })
                except Exception as e:
                    print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

        # Build context
        context_text = "You are CloudLens AI, an expert cloud cost optimization assistant.\n\n"
        
        if billing_context:
            context_text += "User's Cloud Billing Summary:\n"
            for item in billing_context:
                context_text += f"\n{item['provider']}:\n"
                context_text += f"  - Last 30 days: ${item['total_cost_30days']}\n"
                context_text += f"  - Daily average: ${item['daily_average']}\n"
                context_text += f"  - Top services: {', '.join(item['services'])}\n"
        else:
            context_text += "User has not connected any cloud providers yet.\n"

        context_text += f"""
User's question: {user_message}

Keep your response concise (2-3 paragraphs max). Be helpful and focus on cost optimization."""

        # Call OpenRouter API (FREE!)
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:3000',
        }
        
        payload = {
            "model": "meta-llama/llama-2-70b-chat",  # Free model
            "messages": [
                {
                    "role": "system",
                    "content": "You are CloudLens AI, an expert cloud cost optimization assistant. Provide concise, actionable advice about cloud costs."
                },
                {
                    "role": "user",
                    "content": context_text
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        
        print(f"OpenRouter response status: {response.status_code}")
        print(f"OpenRouter response: {response.text}")
        
        if response.status_code != 200:
            return Response(
                {'error': f'API Error: {response.status_code} - {response.text}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        result = response.json()
        
        try:
            ai_response = result['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing response: {str(e)}")
            ai_response = "I couldn't generate a response. Please try again."

        return Response({
            'response': ai_response,
            'billing_summary': billing_context,
            'model': 'llama-2-70b',
            'is_free': True
        }, status=status.HTTP_200_OK)

    except requests.exceptions.Timeout:
        return Response(
            {'error': 'Request timeout. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return Response(
            {'error': f'Error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_carbon_footprint(request):
    """
    Calculate carbon footprint based on cloud usage.
    """
    try:
        provider = request.query_params.get('provider', 'AWS')
        days = int(request.query_params.get('days', 30))
        
        from api.models import CloudConnection, BillingData
        
        try:
            connection = CloudConnection.objects.get(
                user=request.user,
                cloud_provider=provider,
                is_active=True
            )
            
            billing_data = BillingData.objects.filter(
                cloud_connection=connection,
                date__gte=timezone.now() - timedelta(days=days)
            )
            
            carbon_factors = {
                'us-east-1': 380,
                'us-west-2': 100,
                'eu-west-1': 300,
                'ap-south-1': 650,
                'ap-southeast-1': 420,
                'eu-north-1': 50,
                'eu-central-1': 250,
            }
            
            total_cost = billing_data.aggregate(
                total=models.Sum('total_cost')
            )['total'] or 0
            
            estimated_kwh = float(total_cost) * 10
            avg_carbon_factor = carbon_factors.get('ap-south-1', 500)
            
            total_co2_grams = estimated_kwh * avg_carbon_factor
            total_co2_kg = total_co2_grams / 1000
            
            sustainability_score = max(0, min(100, 100 - (total_co2_kg / max(days, 1) * 0.5)))
            
            recommendations = [
                'Switch to renewable-friendly regions like Sweden or Oregon',
                'Use spot instances for non-critical workloads',
                'Enable auto-scaling to reduce idle capacity',
                'Consider consolidating underutilized servers'
            ]
            
            return Response({
                'provider': provider,
                'period_days': days,
                'total_cost': float(total_cost),
                'estimated_kwh': float(estimated_kwh),
                'total_co2_kg': float(total_co2_kg),
                'co2_per_day': float(total_co2_kg / max(days, 1)),
                'sustainability_score': float(sustainability_score),
                'score_category': 'High Emissions' if sustainability_score < 50 else 'Moderate' if sustainability_score < 75 else 'Green Cloud',
                'recommendations': recommendations,
            })
            
        except CloudConnection.DoesNotExist:
            return Response(
                {'error': f'Cloud connection not found for {provider}'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        print(f"Carbon error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )