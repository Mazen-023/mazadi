import os
import logging

# Try to import AI dependencies, handle gracefully if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChatModels:
    """Manages AI models for the chatbot"""

    _instance = None
    _models_loaded = False

    def __new__(cls):
        """Singleton pattern to ensure only one instance of models"""
        if cls._instance is None:
            cls._instance = super(ChatModels, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._models_loaded:
            if TORCH_AVAILABLE:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {self.device}")
            else:
                self.device = "cpu"
                logger.warning("PyTorch not available, using CPU fallback")

            # Initialize models to None - they will be loaded on first use
            self.tokenizer = None
            self.model = None
            self.sentence_model = None

            self.initialize_nltk()
            # Don't load models during startup - load them when needed
            self._models_loaded = True

    def initialize_nltk(self):
        """Initialize NLTK data"""
        if not NLTK_AVAILABLE:
            logger.warning("NLTK not available, skipping initialization")
            return

        try:
            nltk_dir = os.path.expanduser("~/nltk_data")
            if not os.path.exists(nltk_dir):
                os.makedirs(nltk_dir)

            # Download required NLTK data
            nltk.download('punkt', quiet=True, download_dir=nltk_dir)
            nltk.download('stopwords', quiet=True, download_dir=nltk_dir)
            logger.info("NLTK data initialized successfully")
        except Exception as e:
            logger.warning(f"NLTK initialization failed: {e}")

    def load_models(self):
        """Load AI models"""
        # Initialize models to None
        self.tokenizer = None
        self.model = None
        self.sentence_model = None

        if not (TORCH_AVAILABLE and TRANSFORMERS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE):
            logger.warning("AI dependencies not available, models will not be loaded")
            return

        try:
            # Load conversational model
            model_name = "microsoft/DialoGPT-small"
            logger.info(f"Loading conversational model: {model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)

            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load sentence transformer for semantic similarity
            logger.info("Loading sentence transformer model")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

            logger.info("All models loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            # Fallback: set models to None
            self.tokenizer = None
            self.model = None
            self.sentence_model = None

    def generate_response(self, input_text, max_length=100):
        """Generate response using the conversational model"""
        # Load models if not already loaded
        if not self.model or not self.tokenizer:
            self.load_models()

        if not self.model or not self.tokenizer:
            return "Sorry, the AI model is not available right now."

        try:
            # Encode input
            input_ids = self.tokenizer.encode(input_text + self.tokenizer.eos_token, return_tensors='pt').to(self.device)

            # Generate response
            if TORCH_AVAILABLE:
                with torch.no_grad():
                    output = self.model.generate(
                        input_ids,
                        max_length=max_length,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
            else:
                return "AI model not available"

            # Decode response
            response = self.tokenizer.decode(output[0], skip_special_tokens=True)

            # Remove input from response
            if input_text in response:
                response = response.replace(input_text, "").strip()

            return response if response else "I'm not sure how to respond to that."

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while generating a response."

    def is_available(self):
        """Check if models are available"""
        return self.model is not None and self.tokenizer is not None and self.sentence_model is not None


# Global instance
chat_models = ChatModels()
