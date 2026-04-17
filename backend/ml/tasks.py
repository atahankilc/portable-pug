import random
import time

from celery import shared_task


@shared_task
def predict_task(job_id, image_path):
    from .models import MLJob

    try:
        job = MLJob.objects.get(id=job_id)
        job.status = "running"
        job.save()

        time.sleep(2)

        result = {
            "label": random.choice(["cat", "dog", "bird"]),
            "confidence": round(random.uniform(0.80, 0.99), 4),
        }

        job.status = "success"
        job.result = result
        job.save()
        return result
    except Exception as exc:
        from .models import MLJob
        try:
            job = MLJob.objects.get(id=job_id)
            job.status = "failed"
            job.result = {"error": str(exc)}
            job.save()
        except MLJob.DoesNotExist:
            pass
        raise
