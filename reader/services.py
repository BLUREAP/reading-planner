import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
from .models import ReadingSession, Book
from django.db.models import Sum


def fetch_book_data(title: str) -> dict | None:
    """Получает данные через Google Books API"""
    url = "https://www.googleapis.com/books/v1/volumes"
    # Убрали intitle: для более широкого поиска
    params = {"q": title, "maxResults": 1}
    
    print(f"🚀 DEBUG API: Запрос к Google Books: {title}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📡 DEBUG API: Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("totalItems", 0) > 0:
                vol = data["items"][0]["volumeInfo"]
                
                author = ", ".join(vol.get("authors", ["Неизвестный"]))
                pages = vol.get("pageCount") or 300
                
                print(f"✅ DEBUG API: Успех! '{vol.get('title')}' -> {pages} стр.")
                
                return {
                    "title": vol.get("title"),
                    "author": author,
                    "pages": int(pages),
                    "external_id": vol.get("id", "")
                }
            else:
                print(f"️ DEBUG API: Книга не найдена (0 items).")
        else:
            print(f"❌ DEBUG API: Ошибка сервера Google. Текст: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ DEBUG API Exception: {e}")
        
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