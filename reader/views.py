from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from .forms import BookForm
from .services import fetch_book_data, calculate_progress_chart
from .models import Book, ReadingSession


@login_required
def book_list(request):
    """Список книг пользователя"""
    books = request.user.book_set.all()
    return render(request, 'reader/book_list.html', {'books': books})


@login_required
def add_book(request):
    """Добавление книги с интеграцией API"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            
            # 🔹 Интеграция с OpenLibrary API
            if not book.external_id:
                api_data = fetch_book_data(book.title)
                if api_data:
                    book.author = api_data['author']
                    book.total_pages = api_data['pages']
                    book.external_id = api_data['external_id']
                    messages.success(request, '✅ Данные обновлены из OpenLibrary!')
                else:
                    messages.warning(request, '⚠️ Книга не найдена в API. Сохранено как есть.')
            
            book.user = request.user
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
        
    return render(request, 'reader/add_book.html', {'form': form})


@login_required
def book_detail(request, book_id):
    """Детальная страница книги с аналитикой"""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    progress, chart_html, status = calculate_progress_chart(book_id, request.user.id)
    
    return render(request, 'reader/book_detail.html', {
        'book': book,
        'progress': progress,
        'chart_html': chart_html,
        'status': status,
        'today': date.today().isoformat()  # Для поля даты в форме
    })


@login_required
def add_session(request, book_id):
    """Запись прочитанных страниц"""
    if request.method == 'POST':
        date_val = request.POST.get('date')
        pages = request.POST.get('pages_read')
        ReadingSession.objects.create(
            book_id=book_id,
            date=date_val,
            pages_read=int(pages)
        )
        messages.success(request, '📈 Сессия записана!')
    return redirect('book_detail', book_id=book_id)