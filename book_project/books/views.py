from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from .models import Book
import json
import os
import uuid
from django.conf import settings


def home(request):
    """Главная страница с формой добавления книги"""
    return render(request, 'books/home.html')


def add_book(request):
    """Добавление книги в БД или файл"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        year = request.POST.get('year', '').strip()
        janr = request.POST.get('janr', '').strip()
        save_to = request.POST.get('save_to', 'db')  # db или file

        if not all([title, author, year, janr]):
            messages.error(request, 'Заполните все поля')
            return redirect('home')

        try:
            year_int = int(year)
            if year_int < 1800 or year_int > 2030:
                messages.error(request, 'Год должен быть между 1800 и 2030')
                return redirect('home')
        except ValueError:
            messages.error(request, 'Год должен быть числом')
            return redirect('home')

        if save_to == 'db':
            # Сохранение в базу данных с проверкой дубликатов
            try:
                book, created = Book.objects.get_or_create(
                    title=title,
                    author=author,
                    year=year_int,
                    janr=janr,
                    defaults={
                        'title': title,
                        'author': author,
                        'year': year_int,
                        'janr': janr
                    }
                )
                if created:
                    messages.success(request, 'Книга успешно добавлена в базу данных')
                else:
                    messages.warning(request, 'Такая книга уже существует в базе данных')
            except ValidationError as e:
                messages.error(request, str(e))

        else:
            # Сохранение в JSON файл
            files_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
            os.makedirs(files_dir, exist_ok=True)

            filename = f"books_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(files_dir, filename)

            book_data = {
                'title': title,
                'author': author,
                'year': year_int,
                'janr': janr
            }

            # Если файл существует, читаем и добавляем, иначе создаем новый
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []

            # Проверяем дубликаты в файле
            if not any(b.get('title') == title and b.get('author') == author and b.get('year') == year_int and b.get(
                    'janr') == janr for b in data):
                data.append(book_data)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messages.success(request, f'Книга добавлена в файл {filename}')
            else:
                messages.warning(request, 'Такая книга уже существует в файле')

        return redirect('home')

    return redirect('home')


def book_list(request):
    """Список книг из выбранного источника"""
    source = request.GET.get('source', 'db')  # db или files

    if source == 'db':
        books = Book.objects.all().order_by('-created_at')
        return render(request, 'books/book_list.html', {
            'books': books,
            'source': 'db',
            'title': 'Книги из базы данных'
        })
    else:
        # Чтение из JSON файлов
        files_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
        all_books = []

        if os.path.exists(files_dir):
            for filename in os.listdir(files_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(files_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for book in data:
                                    book['source_file'] = filename
                                    all_books.append(book)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

        return render(request, 'books/book_list.html', {
            'books': all_books,
            'source': 'files',
            'title': 'Книги из JSON файлов'
        })


def search_books(request):
    """AJAX поиск книг в базе данных"""
    query = request.GET.get('q', '').strip()

    if query:
        books = Book.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(author__icontains=query) |
            models.Q(janr__icontains=query)
        ).values('id', 'title', 'author', 'year', 'janr')

        books_list = list(books)
        return JsonResponse({'books': books_list})

    return JsonResponse({'books': []})


def edit_book(request, book_id):
    """Редактирование книги"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        year = request.POST.get('year', '').strip()
        janr = request.POST.get('janr', '').strip()

        if not all([title, author, year, janr]):
            messages.error(request, 'Заполните все поля')
            return redirect('edit_book', book_id=book_id)

        try:
            year_int = int(year)
            if year_int < 1800 or year_int > 2030:
                messages.error(request, 'Год должен быть между 1800 и 2030')
                return redirect('edit_book', book_id=book_id)
        except ValueError:
            messages.error(request, 'Год должен быть числом')
            return redirect('edit_book', book_id=book_id)

        # Проверяем дубликаты (исключая текущую книгу)
        if Book.objects.filter(title=title, author=author, year=year_int, janr=janr).exclude(id=book_id).exists():
            messages.error(request, 'Такая книга уже существует')
            return redirect('edit_book', book_id=book_id)

        book.title = title
        book.author = author
        book.year = year_int
        book.janr = janr

        try:
            book.full_clean()
            book.save()
            messages.success(request, 'Книга успешно обновлена')
            return redirect('book_list')
        except ValidationError as e:
            messages.error(request, str(e))

    return render(request, 'books/edit_book.html', {'book': book})


def delete_book(request, book_id):
    """Удаление книги"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга успешно удалена')
        return redirect('book_list')

    return render(request, 'books/delete_confirm.html', {'book': book})


def export_books(request):
    """Экспорт книг из БД в JSON файл"""
    books = Book.objects.all()

    if not books.exists():
        messages.warning(request, 'Нет книг для экспорта')
        return redirect('book_list')

    files_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    os.makedirs(files_dir, exist_ok=True)

    filename = f"export_books_{uuid.uuid4().hex[:8]}.json"
    filepath = os.path.join(files_dir, filename)

    books_data = []
    for book in books:
        books_data.append({
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'janr': book.janr
        })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(books_data, f, ensure_ascii=False, indent=2)

    messages.success(request, f'Экспортировано {len(books_data)} книг в файл {filename}')
    return redirect('book_list')