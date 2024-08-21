from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=200)
    answer_options = models.JSONField(default=list)
    explanation = models.TextField(null=True, blank=True)
    difficulty = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.question_text
    
class StudentQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    num_correct = models.IntegerField(default=0)
    num_incorrect = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.quiz} ({self.score}%)"