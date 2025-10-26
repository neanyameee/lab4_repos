from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-book/', views.add_book, name='add_book'),
    path('books/', views.book_list, name='book_list'),
    path('search/', views.search_books, name='search_books'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('export/', views.export_books, name='export_books'),
    path('json-file/<str:filename>/', views.view_json_file, name='view_json_file'),
]