from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, HttpResponse, redirect, reverse, get_object_or_404
from . import models
from . import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Class-based view, Обработчики классы---------------
from django.contrib import messages
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag


# list № 22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
# Вместо tasks_list()
# благодаря LoginRequiredMixin доступ закрыт логином и паролем (для функции используется декоратор)
class TaskListView(LoginRequiredMixin, ListView):
    model = models.TodoItem
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'


    def get_queryset(self):
        u = self.request.user   # если user не аутентифицирован, то будет AnonymousUser
        return u.tasks.all()    # правда в list он сможет попасть в будущем, если авторизирован



    def filter_tags(self, tags_by_task):
        result = set()
        for i in tags_by_task:
            result.update(i)

        result = list(result)
        result.sort()
        return result


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = self.get_queryset()
        tags = []
        for task in user_tasks:
            tags.append(task.tags.all())

        context['tags'] = self.filter_tags(tags)
        return context
# 22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222



# list № 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
def filter_tags(tags_by_task):
    result = set()
    for i in tags_by_task:
        result.update(i)

    result = list(result)
    result.sort()
    return result

@login_required
def tasks_by_tag(request, tag_slug=None):
    u = request.user
    tasks = models.TodoItem.objects.filter(owner=u).all()
    # or tasks = u.tasks.all()
    tasks_without_tags = list(tasks)


    tag = None
    if tag_slug:                                    # В целом это немного ненужные строчки
        tag = get_object_or_404(Tag, slug=tag_slug)  # хотя может я ошибаюсь (сравни tag и tag_slug)
        tasks = tasks.filter(tags__in=[tag])        # но эта точно нужна)


    # консоль:
    print(f'\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
          f'tag_slug - {tag_slug}\n'
          f'tag - {tag}\n'
          f'tasks - {tasks}\n'
          f'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n')

    all_tags = []
    for t in tasks:
        all_tags.append(list(t.tags.all()))
    all_tags = filter_tags(all_tags)

    context = {'tasks': tasks, 'tag': tag, 'all_tags': all_tags,
               'tasks_without_tags': tasks_without_tags,}

    # консоль:
    print(f'\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n'
          f'request.body - {request.body}'
          
          f'\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n')

    return render(
        request,
        "tasks/list_by_tag.html",
        context,
    )



# 33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333


# Вместо task_create()
class TaskCreateView(LoginRequiredMixin, View):
    def my_render(self, request, form):     # Свой собственный рендер, но по-моему так сложнее
        return render(request, 'tasks/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms.TodoItemForm(request.POST)
        if form.is_valid():
            # form.save() # так мы делали без привязки задач к пользователю
            # НО С ПРИВЯЗКОЙ:
            new_task = form.save(commit=False)  # здесь мы откладываем шаг сохранения в базу (благодаря commit=False)
                                                # и правим объект,
                                                # который мы получили, прежде чем по-настоящему его сохранить.
            new_task.owner = request.user   # owner = наше поле в базе данных ForeignKey
            #                     request.user мы скорее всего достаем с помощью встроенного класса User
            new_task.save()
            form.save_m2m()
            messages.info(request, 'Задача создана')

            # консоль (почему-то у этого request нет метода data, который ревращает в словарь)
            # print('\n\noooooooooooooooooooooooooooooooooooo\n'
            #       f'request.data - {request.data}'
            #       f'\noooooooooooooooooooooooooooooooooooo\n\n')
            # return redirect('/tasks/list')
            return redirect(reverse('tasks:list'))
        # return render(request, 'tasks/create.html', {'form': form})   # без своего рендера
        return self.my_render(request, form)

    def get(self, request, *args, **kwargs):
        form = forms.TodoItemForm()
        # return render(request, 'tasks/create.html', {'form': form})   # без своего рендера
        return self.my_render(request, form)




class TaskEditView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):   # pk передается в post и get запросы вместе с request

        # сначала мы получаем нужную задачу из базы данных с помощью pk
        t = models.TodoItem.objects.get(id=pk)

        # потом кладем эту задачу как instance в форму, c request.POST
        # где форма это обработает и превратит в html теги для нашего шаблона
        form = forms.TodoItemForm(request.POST, instance=t)

        # консоль:
        print(f'\n\n\nforms.TodoItemForm(request.POST, instance=t) - {forms.TodoItemForm(request.POST, instance=t)}\n\n\n')

        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            messages.info(request, 'Задача отредактирована')

            # консоль:
            print(f'pk - {pk}\n\n models.TodoItem.objects.get(id=pk) - {models.TodoItem.objects.get(id=pk)}\n\n'
                  f'request - {request}\n\n new_task - {new_task}\n\n new_task.owner - {new_task.owner}\n\n'
                  f'request.user - {request.user}\n\n'
                  f'request.POST - {request.POST}\n\n')

            return redirect(reverse('tasks:list'))
        return render(request, 'tasks/edit.html', {'form': form, 'tasks': t})


    def get(self, request, pk, *args, **kwargs):
        t = models.TodoItem.objects.get(id=pk)
        form = forms.TodoItemForm(instance=t)
        context = {'form': form, 'task': t}
        return render(request, 'tasks/edit.html', context)





# ++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Очень сложно, но я разобрался)

class TaskExportView(LoginRequiredMixin, View):

    # def filter_tags(self, tags_by_task):
    #     result = set()
    #     for i in tags_by_task:
    #         result.update(i)
    #
    #     result = list(result)
    #     result.sort()
    #     return result

    def generate_body(self, user, priorities):
        q = Q()
        if priorities['prio_high']:                                 # единственное что мне в TaskExportView
            q = q | Q(priority=models.TodoItem.PRIORITY_HIGH)       # осталось непонятно - то, как работает:
                                                                    # q = q | Q(priority=models.TodoItem.PRIORITY_HIGH)
            #консоль:
            print(f'\n\nq - {q}\n\n'
                  f'Q(priority=models.TodoItem.PRIORITY_HIGH) - '
                  f'{Q(priority=models.TodoItem.PRIORITY_HIGH)}\n\n'
                  f'priorities["prio_high"] - {priorities["prio_high"]}\n\n')

        if priorities['prio_med']:
            q = q | Q(priority=models.TodoItem.PRIORITY_MEDIUM)

            # консоль
            print(f'\n\nq - {q}\n\n'
                  f'Q(priority=models.TodoItem.PRIORITY_MEDIUM) - '
                  f'{Q(priority=models.TodoItem.PRIORITY_MEDIUM)}\n\n'
                  f'priorities["prio_med"] - {priorities["prio_med"]}\n\n')

        if priorities['prio_low']:
            q = q | Q(priority=models.TodoItem.PRIORITY_LOW)

            # консоль
            print(f'\n\nq - {q}\n\n'
                  f'Q(priority=models.TodoItem.PRIORITY_LOW) - '
                  f'{Q(priority=models.TodoItem.PRIORITY_LOW)}\n\n'
                  f'priorities["prio_low"] - {priorities["prio_low"]}\n\n'
                  f'type(q) - {type(q)}\n\n'
                  f'type(Q(priority=models.TodoItem.PRIORITY_LOW)) - '
                  f'{type(Q(priority=models.TodoItem.PRIORITY_LOW))}\n\n')

        tasks = models.TodoItem.objects.filter(owner=user).filter(q).all()
        tags = []
        for t in tasks:
            tags.append(t.tags.all())
        tags = filter_tags(tags)

        body = 'Ваши задачи и приоритеты:\n'
        for t in list(tasks):
            if t.is_completed:

                body += f"[x] {t.description} ({t.get_priority_display()}) tags - {t.tags.all()}\n"
            else:

                body += f"[] {t.description} ({t.get_priority_display()}) tags - {list(t.tags.all())}\n"

        if tags:
            tags_str = 'tags: '
            for i in tags:
                tags_str += (str(i.name) + ', ')
            body += f'\n\n{tags_str[:-2]}'

        # консоль:
        print(f'\n\ntasks - {tasks}\n\n'
              f'body - {body}\n\n')

        return body



    def post(self, request, *args, **kwargs):
        form = forms.TodoItemExportForm(request.POST)


        # консоль
        print(f'\n\n======================================'
              f'\nforms.TodoItemExportForm(request.POST) - '
              f'{forms.TodoItemExportForm(request.POST)}\n\n'
              f'request.POST - '
              f'{request.POST}\n'
              f'==========================================\n\n')

        if form.is_valid():
            email = request.user.email
            body = self.generate_body(request.user, form.cleaned_data)

            #консоль
            print(f'\n\n+++++++++++++++++++++++++++++++++++++++++++++'
                  f'\nform.cleaned_data - {form.cleaned_data}\n\n'  # cleaned_data формы TodoItemExportForm
                  f'self.generate_body(request.user, form.cleaned_data) - ' # именно она отправляется в нашем request.POST
                  f'{self.generate_body(request.user, form.cleaned_data)}\n'
                  f'+++++++++++++++++++++++++++++++++++++++++++++++++\n\n')

            send_mail('Задачи', body, settings.EMAIL_HOST_USER, [email])
            messages.success(request, 'Задачи были отправлены на почту %s'% email)

        else:
            messages.error(request, 'Что-то пошло не так, попробуйте еще раз')
        return redirect(reverse('tasks:list'))


    def get(self, request, *args, **kwargs):
        form = forms.TodoItemExportForm()

        # консоль
        print(f'\n\n**********************************'
              f'\nforms.TodoItemExportForm() - '
              f'{forms.TodoItemExportForm()}\n'
              f'************************************\n\n')

        return render(request, 'tasks/export.html', {'form':form})
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++




#     класс с деталями, наследуется от class based view DetailView
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.TodoItem
    template_name = 'tasks/details.html'

    # get_context_data - для добавления тегов в описания (фухх, это было сложно))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        u = self.request.user
        pk = int(self.request.path.split('/')[-1])  # достаем pk вот таким кривым способом (наверняка есть способ лучше)
        # но можно и другим способом
        user_task = list(models.TodoItem.objects.filter(owner=u, pk=self.kwargs['pk'])) #.filter(id=pk))

        print(f'\n\n:::::::::::::::::::::::::::::::::::::::::::::::::::::\n'
              f'self.kwargs - {self.kwargs}'
              f'\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n\n'
        )


        context['tags'] = user_task[0].tags.all()

        # print(f'\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        #       f'\ntype(self.filter_tags(tags)[0] - {type(context["tags"][0])}'
        #       f'\nself.get_queryset() - {user_task[-1].tags.all()}'
        #       f'\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n')
        return context

    # Для эксперимента
    # def get_queryset(self):
    #     u = self.request.user
    #     pk = int(self.request.path.split('/')[-1])
    #
    #     # консоль:
    #     # print(f'\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n'
    #     #       f'request - {self.request}'
    #     #       f'\nlist(self.request) - {list(self.request)}'
    #     #       f'\ndict(self.request) - {dict(self.request)}'
    #     #       f'\nrequest.GET - {self.request.GET}'
    #     #       f'\nrequest.path - {self.request.path.split("/")[-1]}'
    #     #       f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n')
    #
    #     return models.TodoItem.objects.filter(owner=u).filter(id=pk)
    #     # return u.tasks.all().filter(id=pk)
    #     # return u.tasks.all()





# --------------------------------------------------
@login_required
def index(request):
    import random

    # Эксперимент:
    # tags = {t.name : random.randint(1,100) for t in Tag.objects.all()}

    # Вариант с множеством запросов в базу данных при выводе в темплейт:
    # counts = {t.name: t.taggit_taggeditem_items.count for t in Tag.objects.all()}

    # Не забывай что, когда мы присвоили в моделях tags = TaggableManager()
    # то у нас создалась таблица в бд - Tag, с которой можно работать также как и с другой моделькой
    # метод taggit_taggeditem_items - показывает сколько за данным тегом числится задач

    # Но вариант что представлен выше требует для каждого тега в темплейте запрос в базу данных,
    # что может замедлять, при большом количестве тегов, работу приложения
    # Есть многие способы оптимизации - упрощение запросов, кеширование и т.д.
    # Один из них называется Денормализация (гугли django Aggregation)
    # Делается через метод aggregate и annotate. Содержит подфункции в методе Avg, Max, Min, Count
    # Вместо множества запросов в бд получаем один запрос, это и есть Денормализация
    # (гугли денормализация в бд)
    # Работает очень интересно:

    # Вариант через агрегацию (Денормализация)
    counts = Tag.objects.annotate(total_tasks = Count('todoitem')).order_by('-total_tasks')

    # В этом запросе выдача улучшилась за счёт сортировки, то есть при запросе система
    # один раз пробегается по записям, которые удовлетворяют запрос,
    # считаем число тасок и снова проходит по получившейся выборке и сортирует её на базе придуманного поля.

    # Любая функция, вычисляемая по выборке с последующей сортировкой по результату функции,
    # будет медленнее, чем непосредственная выгрузка всех объектов из какой-то базы
    # и сортировка результата по какому-то полю. Такая процедура ускорения называется денормализацией
    # и относится к области техник работы с базами данных.
    # Нужно просто хранить эти счётчики и при необходимости обновлять значения.

    # консоль:
    print(f'\n\n||||||||||||||||||||||||||||||||||||||||||||\n'
          f'Tag.objects.annotate(total_tasks = Count("todoitem")).order_by("-total_tasks")'
          f' - {Tag.objects.annotate(total_tasks = Count("todoitem")).order_by("-total_tasks")}'
          f'\n||||||||||||||||||||||||||||||||||||||||||||||\n\n')

    counts = {t.name : t.total_tasks for t in counts}

    # Сравни в toolbare запросы до и после

    # Задание - создать ссылки на теги

    common_count = Tag.objects.count()
    return render(request, 'tasks/index.html', {'counts' : counts, 'common_count': common_count})

    # return HttpResponse('hello skillfactory')


def complete_task(request, uid):
    t = models.TodoItem.objects.get(id=uid)
    t.is_completed = True

    t.save()
    messages.success(request, 'Задача выполнена')
    print(uid)
    return HttpResponse('OK')


def delete_task(request, uid): #, tag_slug=None):
    t = models.TodoItem.objects.get(id=uid)
    t.delete()
    messages.success(request, 'Задача удалена')


    # if tag_slug:
    #     return redirect(reverse('tasks:list_by_tag')) ---- # чтобы при удалении пользователь
    #                                                       # оставался на странице с тегами

    # messages.error(request, 'check error')
    # messages.info(request, 'check info')
    # messages.warning(request, 'check warning')
    # return redirect('/tasks/list')
    return redirect(reverse('tasks:list'))



# first error
def trigger_error(request):
    result = 1/ 0
    return result


# second error


# def task_create(request):
#     if request.method == 'POST':
#         form = forms.TodoItemForm(request.POST)      # раньше использовалась AddTaskForm
#         if form.is_valid():
#             # cd = form.cleaned_data            # без формы привязанной к модели: TodoItemForm
#             # desc = cd['description']
#             # t = models.TodoItem(description=desc)
#             form.save()
#             return redirect('/tasks/list')
#     else:
#         form = forms.TodoItemForm()
#
#     return render(request, 'tasks/create.html', {'form' : form})


# def add_task(request):              # С формами и модельными формами эта функция больше не нужна
#     if request.method == 'POST':
#         desc = request.POST['description']
#         t = models.TodoItem(description=desc)
#         t.save()
#         return redirect('/tasks/list')
#         return redirect(reverse('tasks:list'))



# list № 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
# def tasks_list(request):
#     all_tasks = models.TodoItem.objects.all()
#     context = {'tasks': all_tasks}
#     return render(request, 'tasks/list.html', context)
# 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111



def console(request):
    print(f'\n\n{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{\n'
          f'dir(models.TodoItem.objects.all())'
          f'{dir(models.TodoItem.objects.all())}'
          f'\n{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{\n\n')

    print(f'\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n'
          f'dir(models.TodoItem.objects)'
          f'{dir(models.TodoItem.objects)}'
          f'\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n\n')
    return HttpResponse('<h1>look in console</h1>')





























# Create your views here.
