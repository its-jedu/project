import csv
import json
from django.core.management.base import BaseCommand
from learning.models import Quiz, Question

class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help=r'C:\Users\stpau\Documents\JEDU\TESLIM\project\ITS')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    quiz = Quiz.objects.get(id=row['quiz_id'])

                    # Check if the question already exists to avoid duplicates
                    question, created = Question.objects.update_or_create(
                        quiz=quiz,
                        question_text=row['question_text'],
                        defaults={
                            'correct_answer': row['correct_answer'],
                            'answer_options': json.loads(row['answer_options']),
                            'explanation': row['explanation']
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added question: {question.question_text}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Updated question: {question.question_text}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))