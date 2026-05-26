from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'total_pages', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'title': 'Название книги',
            'author': 'Автор',
            'total_pages': 'Всего страниц',
            'deadline': 'Дата сдачи (дедлайн)',
        }