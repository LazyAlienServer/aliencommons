from django.tasks import task


def delete_old_logs(level, days):
    return 1


@task
def clear_debug_logs(days=14):
    debug_deleted = delete_old_logs('info', days)
    return {"status": "success", "message": f"{debug_deleted} old debug logs cleared"}


@task
def clear_info_logs(days=30):
    info_deleted = delete_old_logs('info', days)
    return {"status": "success", "message": f"{info_deleted} old info logs cleared"}


@task
def clear_warn_logs(days=90):
    warn_deleted = delete_old_logs('warn', days)
    return {"status": "success", "message": f"{warn_deleted} old warn logs cleared"}
