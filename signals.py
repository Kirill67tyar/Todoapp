from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from tasks.models import TagCount, TodoItem


@receiver(m2m_changed, sender=TodoItem.tags.through)
def task_tags_updated(sender, instance, action, model, **kwargs):
    if action != 'post_add':
        return
    items_model = model.objects.all()


    for m in items_model:
        count = m.taggit_taggeditem_items.count()
        # скорее всего objects
        t = TagCount.objects.filter(tag_id=m.id).first()
        if t is None:
            t = TagCount.objects.get_or_create(
                tag_slug=m.slug,
                tag_name=m.name,
                tag_id=m.id,
                tag_count=count,
            )
        else:
            t.tag_count = count
        t.save()

    print(f'\n\nwhat model? what model? what model?\n'
          f'model - {model}'
          f'\n action - {action}'

          f'\nwhat model? what model? what model?\n\n')

