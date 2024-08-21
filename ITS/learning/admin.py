from django.contrib import admin
from .models import Student, Quiz, Question, StudentQuiz

admin.site.register(Student)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(StudentQuiz)
