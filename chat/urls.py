from django.urls import path
from .views import ChatView, ContractActionView

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("contract/action/", ContractActionView.as_view(), name="chat_contract_action"),
]
