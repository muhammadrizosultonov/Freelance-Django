from django.urls import path
from .views import *

urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("create/", ProjectCreateView.as_view(), name="project_create"),
    path("<int:project_id>/bid/", BidCreateView.as_view(), name="project_bid"),
    path("proposals/", FreelancerProposalsView.as_view(), name="freelancer_proposals"),
    path("jobs/", FreelancerActiveJobsView.as_view(), name="freelancer_jobs"),
    path("earnings/", FreelancerEarningsView.as_view(), name="freelancer_earnings"),
    path("payments/", FreelancerPaymentsView.as_view(), name="freelancer_payments"),
    path("withdraw/", FreelancerWithdrawView.as_view(), name="freelancer_withdraw"),
    path("settings/", FreelancerSettingsView.as_view(), name="freelancer_settings"),
    path("client/projects/", ClientProjectsView.as_view(), name="client_projects"),
    path("client/proposals/", ClientProposalsView.as_view(), name="client_proposals"),
    path("client/payments/", ClientPaymentsView.as_view(), name="client_payments"),
    path("client/reports/", ClientReportsView.as_view(), name="client_reports"),
    path("client/settings/", ClientSettingsView.as_view(), name="client_settings"),
    path("client/contracts/<int:contract_id>/review/", ClientReviewCreateView.as_view(), name="client_review"),
    path("client/bids/<int:bid_id>/<str:action>/", ClientBidActionView.as_view(), name="client_bid_action"),
]
