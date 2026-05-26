import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
from .models import ReadingSession, Book
from django.db.models import Sum


def fetch_book_data(title: str) -> dict | None:
    """Получает метаданные книги через OpenLibrary API"""
    url = "https://openlibrary.org/search.json"
    params = {"title": title, "limit": 1}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Проверяем, нашлась ли хотя бы одна книга
        if data.get("numFound", 0) > 0:
            doc = data["docs"][0]
            
            # Автор: OpenLibrary возвращает список
            authors = doc.get("author_name", [])
            author = authors[0] if authors else "Неизвестный автор"
            
            # Страницы: берём медиану, если нет – первую запись, иначе 300
            pages_raw = doc.get("number_of_pages_median") or doc.get("number_of_pages", [300])
            pages = int(pages_raw[0]) if isinstance(pages_raw, list) else int(pages_raw)
            
            return {
                "title": doc.get("title"),
                "author": author,
                "pages": pages,
                "external_id": doc.get("key", "").replace("/works/", "")
            }
    except Exception as e:
        # Ошибка попадёт в лог PythonAnywhere для отладки
        print(f"❌ OpenLibrary API Error: {e}")
        
    return None


def calculate_progress_chart(book_id, user_id):
    """Рассчитывает прогресс чтения и возвращает HTML-график Plotly"""
    try:
        book = Book.objects.get(id=book_id, user_id=user_id)
    except Book.DoesNotExist:
        return 0, None, "Книга не найдена"

    sessions = ReadingSession.objects.filter(book=book).order_by('date')
    
    if not sessions.exists():
        return 0, None, "Нет данных о сессиях"

    # 1. Подготовка данных для Pandas
    df = pd.DataFrame(list(sessions.values('date', 'pages_read')))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 2. Аналитика: накопительный итог и % прогресса
    df['cumulative_pages'] = df['pages_read'].cumsum()
    current_pages = df['cumulative_pages'].iloc[-1]
    progress_percent = min(100, round((current_pages / book.total_pages) * 100, 1))

    # 3. Построение графика Plotly
    fig = px.line(df, x='date', y='cumulative_pages', 
                  title=f'Прогресс чтения: {book.title}',
                  labels={'date': 'Дата', 'cumulative_pages': 'Прочитано страниц'})
    
    fig.add_hline(y=book.total_pages, line_dash="dash", line_color="red", 
                  annotation_text="Цель (всего страниц)", annotation_position="bottom right")
    
    fig.update_layout(template="plotly_white", height=400)

    # 4. Конвертация в HTML
    chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
    
    return progress_percent, chart_html, "success"