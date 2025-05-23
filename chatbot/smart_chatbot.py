import time
import logging
import random
import uuid
from typing import Dict, List, Tuple, Optional

from .ai_models import chat_models
from .text_processor import TextProcessor
from .knowledge_base import KNOWLEDGE_BASE_AR, KNOWLEDGE_BASE_EN
from .models import ChatConversation, ChatMessage, ChatbotKnowledgeBase

logger = logging.getLogger(__name__)


class SmartChatBot:
    """Main chatbot class that handles conversation logic"""

    def __init__(self, session_id: str = None, user=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.user = user
        self.text_processor = TextProcessor(chat_models.sentence_model)
        self.conversation = self.get_or_create_conversation()
        self.min_confidence_threshold = 0.4

    def get_or_create_conversation(self) -> ChatConversation:
        """Get existing conversation or create new one"""
        try:
            conversation, created = ChatConversation.objects.get_or_create(
                session_id=self.session_id,
                defaults={
                    'user': self.user,
                    'language': 'ar'  # Default to Arabic
                }
            )
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            # Return a temporary conversation object
            return ChatConversation(
                session_id=self.session_id,
                user=self.user,
                language='ar'
            )

    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        return self.text_processor.detect_language(text)

    def get_knowledge_base(self, language: str) -> Dict:
        """Get appropriate knowledge base for language"""
        if language == 'ar':
            return KNOWLEDGE_BASE_AR
        else:
            return KNOWLEDGE_BASE_EN

    def search_knowledge_base(self, user_input: str, language: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Search knowledge base for best matching response"""
        try:
            knowledge_base = self.get_knowledge_base(language)
            processed_input = self.text_processor.preprocess_text(user_input)
            user_input_lower = user_input.lower().strip()

            best_match = None
            highest_score = 0
            best_category = None

            # First, try exact or partial matches for better accuracy
            for category, data in knowledge_base.items():
                for example in data["examples"]:
                    example_lower = example.lower().strip()

                    # Check for exact match
                    if user_input_lower == example_lower:
                        highest_score = 1.0
                        best_match = category
                        best_category = category
                        break

                    # Check for partial match (contains)
                    if user_input_lower in example_lower or example_lower in user_input_lower:
                        partial_score = 0.8
                        if partial_score > highest_score:
                            highest_score = partial_score
                            best_match = category
                            best_category = category

                    # Use semantic similarity
                    similarity = self.text_processor.get_semantic_similarity(
                        processed_input,
                        self.text_processor.preprocess_text(example)
                    )

                    if similarity > highest_score:
                        highest_score = similarity
                        best_match = category
                        best_category = category

                if highest_score == 1.0:  # Found exact match, break early
                    break

            if highest_score > self.min_confidence_threshold:
                responses = knowledge_base[best_match]["responses"]
                response = random.choice(responses)
                return response, highest_score, best_category

            return None, highest_score, None

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return None, 0.0, None

    def search_database_knowledge_base(self, user_input: str, language: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Search database knowledge base for responses"""
        try:
            processed_input = self.text_processor.preprocess_text(user_input)
            kb_entries = ChatbotKnowledgeBase.objects.filter(
                language=language,
                is_active=True
            )

            best_match = None
            highest_score = 0
            best_category = None

            for entry in kb_entries:
                for example in entry.examples:
                    similarity = self.text_processor.get_semantic_similarity(
                        processed_input,
                        self.text_processor.preprocess_text(example)
                    )

                    if similarity > highest_score:
                        highest_score = similarity
                        best_match = entry
                        best_category = entry.category

            if best_match and highest_score > self.min_confidence_threshold:
                response = random.choice(best_match.responses)
                return response, highest_score, best_category

            return None, highest_score, None

        except Exception as e:
            logger.error(f"Error searching database knowledge base: {e}")
            return None, 0.0, None

    def generate_ai_response(self, user_input: str, language: str) -> str:
        """Generate response using AI model"""
        try:
            if chat_models.is_available():
                response = chat_models.generate_response(user_input)
                if response and len(response.strip()) > 0:
                    return response
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")

        # Fallback responses
        if language == 'ar':
            fallback_responses = [
                "عذراً، لم أفهم سؤالك. هل يمكنك إعادة صياغته؟",
                "أعتذر، لست متأكداً من كيفية الإجابة على هذا السؤال.",
                "هل يمكنك توضيح سؤالك أكثر؟"
            ]
        else:
            fallback_responses = [
                "Sorry, I didn't understand your question. Could you rephrase it?",
                "I apologize, I'm not sure how to answer that question.",
                "Could you please clarify your question?"
            ]

        return random.choice(fallback_responses)

    def save_message(self, content: str, message_type: str, response_time: float = None,
                    confidence_score: float = None, knowledge_base_match: str = None):
        """Save message to database"""
        try:
            if hasattr(self.conversation, 'pk') and self.conversation.pk:
                ChatMessage.objects.create(
                    conversation=self.conversation,
                    message_type=message_type,
                    content=content,
                    response_time=response_time,
                    confidence_score=confidence_score,
                    knowledge_base_match=knowledge_base_match
                )
        except Exception as e:
            logger.error(f"Error saving message: {e}")

    def respond(self, user_input: str) -> Dict:
        """Main method to generate chatbot response"""
        start_time = time.time()

        # Validate input
        if not user_input or not user_input.strip():
            error_msg = "الرجاء إدخال نص للرد عليك!" if self.conversation.language == 'ar' else "Please enter some text!"
            return {
                'response': error_msg,
                'confidence': 0.0,
                'response_time': 0.0,
                'language': self.conversation.language,
                'source': 'validation'
            }

        user_input = user_input.strip()

        # Detect language and update conversation
        detected_language = self.detect_language(user_input)
        if self.conversation.language != detected_language:
            self.conversation.language = detected_language
            try:
                if hasattr(self.conversation, 'pk') and self.conversation.pk:
                    self.conversation.save()
            except Exception as e:
                logger.error(f"Error updating conversation language: {e}")

        # Save user message
        self.save_message(user_input, 'user')

        # Try to find response in knowledge base
        response, confidence, category = self.search_knowledge_base(user_input, detected_language)
        source = 'knowledge_base'

        # If no good match in static KB, try database KB
        if not response:
            response, confidence, category = self.search_database_knowledge_base(user_input, detected_language)
            source = 'database_kb'

        # If still no good match, use AI model
        if not response:
            response = self.generate_ai_response(user_input, detected_language)
            confidence = 0.3  # Lower confidence for AI-generated responses
            source = 'ai_model'

        # Calculate response time
        response_time = time.time() - start_time

        # Save bot response
        self.save_message(
            response,
            'bot',
            response_time=response_time,
            confidence_score=confidence,
            knowledge_base_match=category
        )

        return {
            'response': response,
            'confidence': confidence,
            'response_time': response_time,
            'language': detected_language,
            'source': source,
            'category': category
        }

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        try:
            if hasattr(self.conversation, 'pk') and self.conversation.pk:
                messages = self.conversation.messages.all()[:limit]
                return [
                    {
                        'type': msg.message_type,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                        'confidence': msg.confidence_score
                    }
                    for msg in messages
                ]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")

        return []
