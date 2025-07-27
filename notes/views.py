from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from notes.forms import RegisterForm, NoteForm
from notes.models import Note
from notes.services import create_user


def home(request):
    return render(request, 'home.html')

def register(request):
   form = RegisterForm()

   if request.method == 'POST':
       form = RegisterForm(request.POST)
       if form.is_valid():
           username = form.cleaned_data['username']
           password = form.cleaned_data['password']
           email = form.cleaned_data['email']

           create_user(username=username, email=email, password=password)

           return redirect(reverse('login'))

   return render(request, "registration/register.html", {'form': form})
@login_required
def notes_list_view(request):
    notes = Note.objects.filter(user=request.user).only('id', 'title', 'created_at')
    return render(request, 'notes/notes_list.html', {'notes': notes})

@login_required
def create_note_view(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            # создаём заметку напрямую
            note = form.save(commit=False)
            note.user = request.user  # если хочешь связать заметку с пользователем
            note.save()

            # после сохранения перенаправляем на страницу просмотра заметки
            return redirect(reverse('note-view', args=(note.id,)))
    else:
        form = NoteForm()

    return render(request, 'notes/create_note.html', {'form': form})
@login_required
def note_view(request, note_id: int):
    note = get_object_or_404(Note, id=note_id)
    if request.user != note.user:
        return HttpResponseForbidden(content="You are not authorized to view this note.")

    return render(request, 'notes/note.html', {'note': note})
