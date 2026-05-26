from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Book(models.Model):
    """Книга для чтения"""
    title = models.CharField("Название", max_length=200)
    author = models.CharField("Автор", max_length=100, blank=True)
    total_pages = models.PositiveIntegerField("Всего страниц", blank=True, null=True)
    deadline = models.DateField("Дедлайн")
    external_id = models.CharField("ID из OpenLibrary", max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.author})"


class ReadingPlan(models.Model):
    """План чтения книги"""
    book = models.OneToOneField(Book, on_delete=models.CASCADE, verbose_name="Книга")
    start_date = models.DateField("Дата начала")
    daily_target = models.PositiveIntegerField("Страниц в день")
    is_active = models.BooleanField("Активен", default=True)
    
    class Meta:
        verbose_name = "План чтения"
        verbose_name_plural = "Планы чтения"
    
    def __str__(self):
        return f"План для {self.book.title}"


class ReadingSession(models.Model):
    """Сессия чтения"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга", related_name='sessions')
    date = models.DateField("Дата", default=timezone.now)
    pages_read = models.PositiveIntegerField("Прочитано страниц")
    notes = models.TextField("Заметки", blank=True)
    
    class Meta:
        verbose_name = "Сессия чтения"
        verbose_name_plural = "Сессии чтения"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.book.title} - {self.pages_read} стр. ({self.date})"