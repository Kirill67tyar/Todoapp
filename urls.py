from django.conf.urls import url
from . import views
from django.urls import path, include

app_name = 'tasks'

urlpatterns = [
    path('', views.index, name='index'),

    # Если нам нужно отображение тегов, и теги как ссылки, раскомментить эти два пути для листа
    # Attention! теги не русифицированы, не создавать теги на русском
    path("list/", views.tasks_by_tag, name="list"), # list № 3
    path("list/tag/<slug:tag_slug>", views.tasks_by_tag, name="list_by_tag"), # list № 3

    # Если нам нужен список без тегов, раскомментить этот путь для листа:
    # path('list/', views.TaskListView.as_view(), name='list'),   # list № 2   # http://127.0.0.1:8000/tasks/list/

    path('create/', views.TaskCreateView.as_view(), name='create'),  # http://127.0.0.1:8000/tasks/create/
    # path('list/', views.tasks_list, name='list'),  # list № 1 # http://127.0.0.1:8000/tasks/list/
    # path('create/', views.task_create, name='create'),  # http://127.0.0.1:8000/tasks/create/
    # path('add-task/', views.add_task, name='api-add-task'),
    path('complete/<int:uid>', views.complete_task, name='complete'),
    path('delete/<int:uid>', views.delete_task, name='delete'),
    path('delete/<int:uid>/<slug:tag_slug>', views.delete_task, name='delete'),
    path('details/<int:pk>', views.TaskDetailView.as_view(), name='details'),
    path('edit/<int:pk>', views.TaskEditView.as_view(), name='edit'),
    path('export/', views.TaskExportView.as_view(), name='export'),
    path('console/', views.console, name='console'),

]






































