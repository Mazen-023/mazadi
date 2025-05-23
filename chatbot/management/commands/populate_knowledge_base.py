from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledgeBase
from chatbot.knowledge_base import KNOWLEDGE_BASE_AR, KNOWLEDGE_BASE_EN


class Command(BaseCommand):
    help = 'Populate the chatbot knowledge base with predefined data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing knowledge base before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing knowledge base...')
            ChatbotKnowledgeBase.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Knowledge base cleared.'))

        # Populate Arabic knowledge base
        self.stdout.write('Populating Arabic knowledge base...')
        for category, data in KNOWLEDGE_BASE_AR.items():
            kb_entry, created = ChatbotKnowledgeBase.objects.get_or_create(
                category=category,
                language='ar',
                defaults={
                    'examples': data['examples'],
                    'responses': data['responses'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {category} (Arabic)')
            else:
                # Update existing entry
                kb_entry.examples = data['examples']
                kb_entry.responses = data['responses']
                kb_entry.save()
                self.stdout.write(f'  Updated: {category} (Arabic)')

        # Populate English knowledge base
        self.stdout.write('Populating English knowledge base...')
        for category, data in KNOWLEDGE_BASE_EN.items():
            kb_entry, created = ChatbotKnowledgeBase.objects.get_or_create(
                category=category,
                language='en',
                defaults={
                    'examples': data['examples'],
                    'responses': data['responses'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created: {category} (English)')
            else:
                # Update existing entry
                kb_entry.examples = data['examples']
                kb_entry.responses = data['responses']
                kb_entry.save()
                self.stdout.write(f'  Updated: {category} (English)')

        # Create some default settings
        self.stdout.write('Creating default chatbot settings...')
        default_settings = [
            {
                'key': 'confidence_threshold',
                'value': '0.6',
                'description': 'Minimum confidence score for knowledge base matches'
            },
            {
                'key': 'max_response_length',
                'value': '500',
                'description': 'Maximum length of chatbot responses'
            },
            {
                'key': 'enable_ai_fallback',
                'value': 'true',
                'description': 'Enable AI model fallback when no knowledge base match found'
            },
            {
                'key': 'default_language',
                'value': 'ar',
                'description': 'Default language for new conversations'
            }
        ]

        from chatbot.models import ChatbotSettings
        for setting in default_settings:
            setting_obj, created = ChatbotSettings.objects.get_or_create(
                key=setting['key'],
                defaults={
                    'value': setting['value'],
                    'description': setting['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created setting: {setting["key"]}')
            else:
                self.stdout.write(f'  Setting exists: {setting["key"]}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated knowledge base with '
                f'{len(KNOWLEDGE_BASE_AR)} Arabic and {len(KNOWLEDGE_BASE_EN)} English categories'
            )
        )
