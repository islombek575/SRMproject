from django.urls import path
from reports.views import dashboard_view, sales_history

app_name = "reports"

urlpatterns = [
    path("", dashboard_view, name="reports_report"),
    path("history/", sales_history, name="history"),
]