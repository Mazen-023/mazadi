import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator

from .smart_chatbot import SmartChatBot
from .models import ChatConversation, ChatMessage

logger = logging.getLogger(__name__)


class ChatView(View):
    """Main chat interface view"""

    def get(self, request):
        """Render chat interface"""
        return render(request, 'chatbot/chat.html')


class ChatAPIView(View):
    """API endpoint for chat interactions"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Handle chat message and return bot response"""
        try:
            # Parse request data
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')

            if not user_message:
                return JsonResponse({
                    'error': 'Message is required',
                    'success': False
                }, status=400)

            # Get user if authenticated
            user = request.user if request.user.is_authenticated else None

            # Create chatbot instance
            chatbot = SmartChatBot(session_id=session_id, user=user)

            # Get response
            response_data = chatbot.respond(user_message)

            return JsonResponse({
                'success': True,
                'response': response_data['response'],
                'confidence': response_data['confidence'],
                'response_time': response_data['response_time'],
                'language': response_data['language'],
                'source': response_data['source'],
                'session_id': chatbot.session_id
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        except Exception as e:
            logger.error(f"Error in chat API: {e}")
            return JsonResponse({
                'error': 'Internal server error',
                'success': False
            }, status=500)


@login_required
def chat_history(request):
    """View chat history for authenticated users"""
    try:
        conversations = ChatConversation.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')

        paginator = Paginator(conversations, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'chatbot/history.html', {
            'conversations': page_obj
        })

    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return render(request, 'chatbot/history.html', {
            'conversations': [],
            'error': 'Error loading chat history'
        })


@login_required
def conversation_detail(request, conversation_id):
    """View detailed conversation"""
    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        messages = conversation.messages.all().order_by('timestamp')

        return render(request, 'chatbot/conversation_detail.html', {
            'conversation': conversation,
            'messages': messages
        })

    except ChatConversation.DoesNotExist:
        return render(request, 'chatbot/conversation_detail.html', {
            'error': 'Conversation not found'
        })
    except Exception as e:
        logger.error(f"Error loading conversation detail: {e}")
        return render(request, 'chatbot/conversation_detail.html', {
            'error': 'Error loading conversation'
        })


@require_http_methods(["GET"])
def chat_widget(request):
    """Return chat widget HTML for embedding"""
    return render(request, 'chatbot/widget.html')


@csrf_exempt
@require_http_methods(["POST"])
def chat_feedback(request):
    """Handle user feedback on chat responses"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        feedback = data.get('feedback')  # 'helpful' or 'not_helpful'

        if not message_id or feedback not in ['helpful', 'not_helpful']:
            return JsonResponse({
                'error': 'Invalid feedback data',
                'success': False
            }, status=400)

        # Here you could save feedback to database
        # For now, just log it
        logger.info(f"Feedback received for message {message_id}: {feedback}")

        return JsonResponse({
            'success': True,
            'message': 'Feedback received'
        })

    except Exception as e:
        logger.error(f"Error handling feedback: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'success': False
        }, status=500)
