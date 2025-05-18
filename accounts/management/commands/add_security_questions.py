from django.core.management.base import BaseCommand
from accounts.models import SecurityQuestion

class Command(BaseCommand):
    help = 'Adds default security questions to the database'

    def handle(self, *args, **options):
        # List of default security questions
        questions = [
            "What was the name of your first pet?",
            "What was the name of your first school?",
            "What is your mother's maiden name?",
            "In what city were you born?",
            "What was your childhood nickname?",
            "What is the name of your favorite childhood friend?",
            "What street did you live on in third grade?",
            "What is the middle name of your oldest child?",
            "What is your oldest sibling's birthday month and year? (e.g., January 1990)",
            "What is the make and model of your first car?",
            "What was your favorite food as a child?",
            "Where did you meet your spouse/significant other?",
            "What is your favorite movie?",
            "What is your favorite book?",
            "What is the name of the hospital where you were born?",
        ]
        
        # Add questions to the database if they don't already exist
        count = 0
        for question in questions:
            if not SecurityQuestion.objects.filter(question=question).exists():
                SecurityQuestion.objects.create(question=question)
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} security questions'))
