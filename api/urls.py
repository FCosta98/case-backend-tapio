from django.urls import path
from .views import ReportList, ReportDetail, SourceList, SourceDetail

#endpoints
urlpatterns = [
    path('reports/', ReportList.as_view()),
    path('reports/<int:report_id>/', ReportDetail.as_view()),
    path('sources/', SourceList.as_view()),
    path('sources/<int:source_id>/', SourceDetail.as_view()),
]
 