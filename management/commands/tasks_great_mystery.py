from django.core.management import BaseCommand
from tasks.models import TodoItem
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = u"poh voobshe"

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='input_file', type=str)

    def handle(self, *args, **options):
        data = {}
        for u in User.objects.all():
            data['u'] = {'completed':[], 'not_completed':[]}
            for t in u.tasks.all():
                if t.is_completed:
                    data['u']['completed'].append(t)
                else:
                    data['u']['not_completed'].append(t)
        print(*data.items(),sep='\n')
        directory = "../../../task_11_5_1.txt"
        # посмотреть как это выглядит в файле
        with open(directory, 'w') as f:
            for i in data.items():
                f.write(str(i)+'\n')

# python manage.py tasks_great_mystery