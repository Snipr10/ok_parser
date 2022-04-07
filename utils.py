from django.utils import timezone


def update_only_time(task, attempt=0):
    try:
        from accounts import update_time_timezone
        task.last_modified = update_time_timezone(timezone.localtime())
        task.save(update_fields=['last_modified'])
    except Exception as e:
        attempt += 1
        if attempt < 6:
            update_only_time(task, attempt=attempt)
