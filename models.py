from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class TodoItem(models.Model):

    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3

    PRIORITY_CHOICES = (
        (PRIORITY_HIGH, 'Высокий приоритет'),
        (PRIORITY_MEDIUM, 'Средний приоритет'),
        (PRIORITY_LOW, 'Низкий приоритет'),
    )

    description = models.CharField(max_length=64,)
    is_completed = models.BooleanField('выполнено', default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
# благодаря аргументу related_name (связанное имя) в поле ForeignKey мы можем обращаться к
# модели (в данном случае User), к которой мы привязали нашу модель.
# В данном случае обращение будет выглядить как u = request.user -> u.tasks.all()
# Эта tasks благодаря related_name

    priority = models.IntegerField('Приоритет', choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    tags = TaggableManager()

    # у полей с аргументом choices есть полезный метод отображения через интерфейс а не базу

    # t = TodoItem.objects.all()[1]

    # отображение через базу:
    # t.priority (t.name_field_in_bd)

    # отображение через интерфейс, как это видит пользователь:
    # t.get_priority_display() (t.get_nameFieldInBd_display())

    def __str__(self):
        return self.description.lower()

    class Meta:
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('tasks:details', args=[self.pk])


class TagCount(models.Model):
    tag_slug = models.CharField(max_length=128)
    tag_name = models.CharField(max_length=128)
    tag_id = models.PositiveIntegerField(default=0)
    tag_count = models.PositiveIntegerField(db_index=True, default=0)



























# Create your models here.
