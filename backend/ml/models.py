from django.db import models


class MLJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    task_id = models.CharField(max_length=255, unique=True)
    task_type = models.CharField(max_length=100, default="image_classification")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    image = models.ImageField(upload_to="uploads/")
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MLJob({self.task_id}, {self.status})"
