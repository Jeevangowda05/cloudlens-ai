from django.urls import path

from .views import CostReportView, CostSimulationView, IdleResourcesView, RegionAdvisorView, TagCostAllocationView

urlpatterns = [
    path('simulate/', CostSimulationView.as_view(), name='simulate'),
    path('regions/', RegionAdvisorView.as_view(), name='regions'),
    path('idle-resources/', IdleResourcesView.as_view(), name='idle-resources'),
    path('reports/', CostReportView.as_view(), name='reports'),
    path('tags/', TagCostAllocationView.as_view(), name='tags'),
]
