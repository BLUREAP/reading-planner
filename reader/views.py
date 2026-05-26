from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from .forms import BookForm
from .services import fetch_book_data
from .models import Book, ReadingSession


@login_required
def book_list(request):
    books = request.user.book_set.all()
    return render(request, 'reader/book_list.html', {'books': books})


@login_required
def add_book(request):
    print(f"🔍 DEBUG VIEW: Метод запроса: {request.method}")
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        print(f"🔍 DEBUG VIEW: Форма валидна? {form.is_valid()}")
        
        if form.is_valid():
            book = form.save(commit=False)
            print(f"🔍 DEBUG VIEW: external_id книги: '{book.external_id}'")
            print(f"🔍 DEBUG VIEW: Пытаемся вызвать API для '{book.title}'...")
            
            if not book.external_id:
                print("🚀 DEBUG VIEW: Вызываем fetch_book_data...")
                api_data = fetch_book_data(book.title)
                
                if api_data:
                    print(f"✅ DEBUG VIEW: API вернул данные: {api_data}")
                    book.author = api_data['author']
                    book.total_pages = api_data['pages']
                    book.external_id = api_data['external_id']
                    messages.success(request, '✅ Данные подтянуты из API!')
                else:
                    print("❌ DEBUG VIEW: API вернул None")
                    messages.warning(request, '⚠️ API не ответил. Сохранено вручную.')
            else:
                print("ℹ️ DEBUG VIEW: external_id уже заполнен, пропускаем API")
            
            book.user = request.user
            book.save()
            print(f"💾 DEBUG VIEW: Книга сохранена в БД (ID: {book.id})")
            return redirect('book_list')
        else:
            print(f"❌ DEBUG VIEW: Ошибки формы: {form.errors}")
    else:
        form = BookForm()
        
    return render(request, 'reader/add_book.html', {'form': form})


@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    from .services import calculate_progress_chart
    progress, chart_html, status = calculate_progress_chart(book_id, request.user.id)
    
    agg = ReadingSession.objects.filter(book=book).aggregate(total=Sum('pages_read'))
    total_read = agg['total'] or 0
    
    return render(request, 'reader/book_detail.html', {
        'book': book,
        'progress': progress,
        'chart_html': chart_html,
        'status': status,
        'today': date.today().isoformat