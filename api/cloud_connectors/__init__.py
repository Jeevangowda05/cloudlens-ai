"""
Cloud Connector Factory
Switches between mock and real connectors based on Django settings
This allows easy toggling between demo mode and production mode
"""

from django.conf import settings


class ConnectorFactory:
    """
    Factory pattern to create appropriate cloud connectors.
    
    Uses the USE_MOCK_CLOUD_APIS setting to determine whether to return
    mock connectors (for demos/testing) or real connectors (for production).
    """
    
    @staticmethod
    def get_connector(provider: str):
        """
        Get cloud connector based on Django settings.
        
        Args:
            provider (str): Cloud provider - 'AWS', 'AZURE', or 'GCP'
        
        Returns:
            Connector instance (Mock or Real based on USE_MOCK_CLOUD_APIS setting)
        
        Raises:
            ValueError: If provider is not recognized
        
        Example:
            >>> connector = ConnectorFactory.get_connector('AWS')
            >>> billing_data = connector.get_billing_data(days=30)
        """
        
        # Import mock connectors
        from .mock_connector import (
            MockAWSConnector,
            MockAzureConnector,
            MockGCPConnector
        )
        
        # In demo/mock mode, return mock connectors
        if getattr(settings, 'USE_MOCK_CLOUD_APIS', True):
            if provider == 'AWS':
                return MockAWSConnector()
            elif provider == 'AZURE':
                return MockAzureConnector()
            elif provider == 'GCP':
                return MockGCPConnector()
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        # In production mode, return real connectors
        # (These will be implemented when real credentials are available)
        else:
            # Placeholder for real connectors
            raise NotImplementedError(
                f"Real connector for {provider} not yet implemented. "
                f"Set USE_MOCK_CLOUD_APIS=True to use mock data."
            )


__all__ = ['ConnectorFactory']
