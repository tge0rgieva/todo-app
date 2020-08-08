from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import TodoForm
from .models import Todo


def home(request):
    return render(request, 'todo/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', {'user_creation_form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],
                                                password=request.POST['password1'])
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signup_user.html', {'user_creation_form': UserCreationForm(),
                                                                 'error': 'The username is already used'})

            user.save()
        else:
            return render(request, 'todo/signup_user.html', {'user_creation_form': UserCreationForm(),
                                                             'error': 'Passwords did not match'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/login_user.html', {'authentication_form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/login_user.html', {'authentication_form': AuthenticationForm(),
                                                            'error': 'User and password did not match.'})
        else:
            login(request, user)
            return redirect('home')


@login_required
def logout_user(request):
    # We only want to logout someone if it is POST request.
    # Otherwise the browser may logout the user when initially checking the urls in the HTML.
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/current_todos.html', {'todos': todos})


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completed_todos.html', {'todos': todos})


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'todo_form': TodoForm})
    # If the user submit a POST request
    else:
        try:
            # The view creates an instance of TodoForm and populates it with the data from the POST request.
            # The POST method bundles up the form data before encoding it and sending it to the server.
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html', {
                'todo_form': TodoForm(),
                'error': 'Bad data passed. Try again'
            })


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/view_todo.html', {'todo': todo, 'todo_form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            if todo.date_completed is None:
                return redirect('current_todos')
            else:
                return redirect('completed_todos')
        except ValueError:
            return render(request, 'todo/view_todo.html', {'todo': todo,
                                                           'todo_form': form,
                                                           'error': 'Bad data'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        if todo.date_completed is None:
            return redirect('current_todos')
        else:
            return redirect('completed_todos')
