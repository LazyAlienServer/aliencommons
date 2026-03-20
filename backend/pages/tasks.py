from django.tasks import task

from core.utils.youtube import fetch_youtube_data


@task
def refresh_youtube_cache():
    try:
        fetch_youtube_data()
        return {"status": "success", "message": "YouTube channel data successfully refreshed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
