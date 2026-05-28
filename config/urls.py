from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', include('reader.urls')),  # Подключаем маршруты приложения
]