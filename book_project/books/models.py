from django.db import models
from django.core.exceptions import ValidationError


def validate_year(value):
    if value < 1800 or value > 2030:
        raise ValidationError('Год должен быть между 1800 и 2030')


class Book(models.Model):

    title = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=100, verbose_name='Автор')
    year = models.IntegerField(verbose_name='Год издания', validators=[validate_year])
    janr = models.CharField(max_length=50, verbose_name='Жанр', default='Роман')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['title', 'author', 'year', 'janr']
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
