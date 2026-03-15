from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Conversation, Message
from users.models import CustomUser
from service.models import Contract
from service.forms import ReviewForm

class ChatView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        user_param = request.GET.get("user")
        active_conversation = None
        if user_param:
            other_user = get_object_or_404(CustomUser, id=user_param)
            if other_user != request.user:
                active_conversation = Conversation.get_or_create_between(request.user, other_user)

        active_contracts = Contract.objects.filter(
            status=Contract.StatusChoices.ACTIVE
        ).filter(Q(client=request.user) | Q(freelancer=request.user)).select_related(
            "client", "freelancer"
        )
        for contract in active_contracts:
            other_user = contract.freelancer if contract.client_id == request.user.id else contract.client
            Conversation.get_or_create_between(request.user, other_user)

        conversations = Conversation.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).select_related("user1", "user2")

        conv_list = []
        for conv in conversations:
            conv.other_user = conv.get_other_user(request.user)
            conv.last_message = conv.messages.order_by("-created_at").first()
            conv.unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
            conv_list.append(conv)

        conv_list.sort(
            key=lambda c: c.last_message.created_at if c.last_message else c.created_at,
            reverse=True,
        )

        if not active_conversation and conv_list:
            active_conversation = conv_list[0]

        active_messages = []
        active_user = None
        active_contract = None
        if active_conversation:
            active_user = active_conversation.get_other_user(request.user)
            contract_qs = Contract.objects.filter(
                Q(client=request.user, freelancer=active_user)
                | Q(client=active_user, freelancer=request.user)
            ).select_related("project")
            active_contract = (
                contract_qs.filter(status=Contract.StatusChoices.ACTIVE).order_by("-created_at").first()
                or contract_qs.order_by("-created_at").first()
            )
            active_messages = (
                Message.objects.filter(conversation=active_conversation)
                .select_related("sender")
                .order_by("created_at")
            )
            Message.objects.filter(
                conversation=active_conversation,
                is_read=False,
            ).exclude(sender=request.user).update(is_read=True)

        context = {
            "conversations": conv_list,
            "active_conversation_id": active_conversation.id if active_conversation else None,
            "active_user": active_user,
            "active_messages": active_messages,
            "active_contract": active_contract,
        }
        return render(request, 'chat.html', context)

    def post(self, request):
        conversation_id = request.POST.get("conversation_id")
        message_text = (request.POST.get("message") or "").strip()
        if not conversation_id or not message_text:
            return redirect("chat")

        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in (conversation.user1, conversation.user2):
            return redirect("chat")

        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=message_text,
        )
        other_user = conversation.get_other_user(request.user)
        return redirect(f"{reverse('chat')}?user={other_user.id}")


class ContractActionView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        contract_id = request.POST.get("contract_id")
        raw_action = (request.POST.get("status_action") or "").strip().lower()
        status_map = {
            "finished": Contract.StatusChoices.FINISHED,
            "cancelled": Contract.StatusChoices.CANCELLED,
            Contract.StatusChoices.FINISHED.lower(): Contract.StatusChoices.FINISHED,
            Contract.StatusChoices.CANCELLED.lower(): Contract.StatusChoices.CANCELLED,
        }
        action = status_map.get(raw_action)
        if not action:
            messages.error(request, "Noto'g'ri amal.")
            return redirect("chat")

        contract = get_object_or_404(Contract, id=contract_id, client=request.user)
        other_user = contract.freelancer

        if contract.status != action:
            contract.status = action
            contract.save(update_fields=["status", "updated_at"])
            if action == Contract.StatusChoices.FINISHED:
                messages.success(request, "Shartnoma yakunlandi.")
            else:
                messages.success(request, "Shartnoma bekor qilindi.")

        rating = (request.POST.get("rating") or "").strip()
        if rating and not hasattr(contract, "review"):
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.contract = contract
                review.client = request.user
                review.freelancer = contract.freelancer
                review.save()
                messages.success(request, "Sharh saqlandi.")
            else:
                messages.error(request, "Sharh ma'lumotlari noto'g'ri.")
        elif rating and hasattr(contract, "review"):
            messages.info(request, "Bu shartnoma uchun sharh allaqachon mavjud.")

        return redirect(f"{reverse('chat')}?user={other_user.id}")
