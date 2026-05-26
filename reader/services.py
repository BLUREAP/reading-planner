import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
from .models import ReadingSession, Book
from django.db.models import Sum


def fetch_book_data(title: str) -> dict | None:
    """Получает метаданные книги через Google Books API (надежнее для страниц)"""
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"intitle:{title}", "maxResults": 1}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("totalItems", 0) > 0:
            vol = data["items"][0]["volumeInfo"]
            
            # Автор
            authors = vol.get("authors", [])
            author = ", ".join(authors) if authors else "Неизвестный автор"
            
            # Страницы (Google Books почти всегда отдаёт точное число)
            pages = vol.get("pageCount")
            if pages is None:
                pages = 300
                print(f"ℹ️ DEBUG: Google Books не вернул pageCount для '{title}'. Установлено 300.")
            else:
                print(f"✅ DEBUG: '{title}' -> {pages} стр. (Google Books)")
                
            return {
                "title": vol.get("title"),
                "author": author,
                "pages": int(pages),
                "external_id": vol.get("id", "")
            }
    except Exception as e:
        print(f"❌ API Error: {e}")
        
    return None


def calculate_progress_chart(book_id, user_id):
    """Рассчитывает прогресс и возвращает HTML-график"""
    try:
        book = Book.objects.get(id=book_id, user_id=user_id)
    except Book.DoesNotExist:
        return 0, None, "Книга не найдена"

    sessions = ReadingSession.objects.filter(book=book).order_by('date')
    if not sessions.exists():
        return 0, None, "Нет данных"

    df = pd.DataFrame(list(sessions.values('date', 'pages_read')))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    df['cumulative_pages'] = df['pages_read'].cumsum()
    current_pages = df['cumulative_pages'].iloc[-1]
    progress_percent = min(100, round((current_pages / book.total_pages) * 100, 1))

    fig = px.line(df, x='date', y='cumulative_pages', 
                  title=f'Прогресс: {book.title}',
                  labels={'date': 'Дата', 'cumulative_pages': 'Прочитано страниц'})
    
    fig.add_hline(y=book.total_pages, line_dash="dash", line_color="red", 
                  annotation_text="Цель", annotation_position="bottom right")
    fig.update_layout(template="plotly_white", height=400)

    chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
    return progress_percent, chart_html, "success"