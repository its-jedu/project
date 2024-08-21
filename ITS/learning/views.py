from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, StudentQuiz, Student
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import views as auth_views
from django.contrib.auth import login
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import urllib.parse
from django.db.models import Q, F, ExpressionWrapper, FloatField
from django.contrib.auth.views import LoginView, LogoutView

# Custom LoginView
class CustomLoginView(LoginView):
    template_name = 'login.html'
    def form_valid(self, form):
        # Log the user in
        response = super().form_valid(form)

        # Ensure the Student object exists
        user = self.request.user
        if not hasattr(user, 'student'):
            Student.objects.create(user=user, name=user.username, email=user.email)

        if 'registration_success' in self.request.session:
            messages.success(self.request, self.request.session.pop('registration_success'))
        return response

# Custom LogoutView
class CustomLogoutView(LogoutView):
    next_page = 'login'  # Redirect to login page after logout

    def dispatch(self, request, *args, **kwargs):
        # Set the logout message
        messages.add_message(request, messages.SUCCESS, f'User {request.user.username} successfully logged out!')
        
        # Proceed with the logout
        response = super().dispatch(request, *args, **kwargs)
        
        # After logout, clear the session and redirect to the login page
        request.session.flush()
        return response
    

@login_required
def home(request):
    student_quizzes = StudentQuiz.objects.filter(student=request.user.student)
    quiz_labels = [quiz.quiz.title for quiz in student_quizzes]
    quiz_scores = [quiz.score for quiz in student_quizzes]

    context = {
        'quiz_labels': quiz_labels,
        'quiz_scores': quiz_scores,
    }

    return render(request, 'dashboard.html', context)

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    # Ensure the user has a Student object
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = Student.objects.create(user=request.user, name=request.user.username, email=request.user.email)

    if request.method == "POST":
        correct_answers = 0
        incorrect_answers = 0
        results = []

        # Get the time taken from the form
        time_taken = float(request.POST.get('time_taken', 0))

        # Check each answer provided by the user
        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            is_correct = selected_answer == question.correct_answer
            if is_correct:
                correct_answers += 1
            else:
                incorrect_answers += 1

            # Append the result for each question
            results.append({
                'question_text': question.question_text,
                'selected_answer': selected_answer,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'is_correct': is_correct,
            })

        # Calculate the score
        score = correct_answers / len(questions) * 100

        # Save the quiz attempt
        student_quiz = StudentQuiz(
            student=student,
            quiz=quiz,
            score=score,
            num_correct=correct_answers,
            num_incorrect=incorrect_answers,
            completed_at=timezone.now(),
            time_taken=time_taken
        )
        student_quiz.save()

        # Calculate if the user is topping the quiz
        better_or_equal_scores = StudentQuiz.objects.filter(
            Q(quiz=quiz) & Q(score__gte=score)
        )
        topping_students = better_or_equal_scores.annotate(
            faster=ExpressionWrapper(
                F('time_taken') - time_taken, output_field=FloatField()
            )
        ).filter(score=score, faster__gt=0).count()

        is_topping = topping_students == 0

        # Get the leaderboard for this quiz
        leaderboard = StudentQuiz.objects.filter(quiz=quiz).order_by('-score', 'time_taken')[:10]

        # Provide feedback in the result page
        return render(request, 'quiz_result.html', {
            'score': score,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'total_questions': len(questions),
            'results': results,
            'time_taken': time_taken,
            'average_time_per_question': time_taken / len(questions),
            'is_topping': is_topping,
            'leaderboard': leaderboard
        })

    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            request.session['registration_success'] = f'Account created for {username}!'
            return redirect('login')
        else:
           print(form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def student_progress(request):
    student_quizzes = StudentQuiz.objects.filter(student=request.user.student)
    scores = [sq.score for sq in student_quizzes]
    dates = [sq.completed_at for sq in student_quizzes]

    # Create a plot
    plt.plot(dates, scores)
    plt.title('Quiz Performance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Score')

    # Save plot to a string buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    return render(request, 'progress.html', {'data': uri})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def dashboard(request):
    # Ensure the user has a student object
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = Student.objects.create(user=request.user, name=request.user.username, email=request.user.email)

    student_quizzes = StudentQuiz.objects.filter(student=request.user.student)
    quiz_labels = [quiz.quiz.title for quiz in student_quizzes]
    quiz_scores = [quiz.score for quiz in student_quizzes]

    context = {
        'quiz_labels': quiz_labels,
        'quiz_scores': quiz_scores,
    }

    return render(request, 'dashboard.html', context)

@login_required
def quiz_list(request):
    # Define the topics with corresponding quiz IDs
    topics = [
        {'name': 'Python', 'description': 'Python Programming Language', 'quiz_id': 1},
        {'name': 'Java', 'description': 'Java Programming Language', 'quiz_id': 2},
        {'name': 'JavaScript', 'description': 'JavaScript Programming Language', 'quiz_id': 3},
        {'name': 'C', 'description': 'C Programming Language', 'quiz_id': 4}
    ]

    return render(request, 'quiz_list.html', {'topics': topics})

@login_required
def previous_quizzes(request):
    # Order the student quizzes by the most recent first
    student_quizzes = StudentQuiz.objects.filter(student=request.user.student).order_by('-completed_at')
    return render(request, 'previous_quizzes.html', {'student_quizzes': student_quizzes})

@login_required
def leaderboard(request):
    # Assuming you want to show the top scoring students or similar logic
    top_students = StudentQuiz.objects.order_by('-score')[:10]  # Top 10 students
    return render(request, 'leaderboard.html', {'top_students': top_students})
