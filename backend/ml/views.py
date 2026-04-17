import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MLJob
from .serializers import MLJobSerializer
from .tasks import predict_task


class UploadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"detail": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        task_id = str(uuid.uuid4())
        job = MLJob.objects.create(
            task_id=task_id,
            image=image,
        )

        predict_task.delay(job.id, job.image.path)

        job.refresh_from_db()
        return Response(MLJobSerializer(job).data, status=status.HTTP_201_CREATED)


class StatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, task_id):
        try:
            job = MLJob.objects.get(task_id=task_id)
        except MLJob.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(MLJobSerializer(job).data)


class ResultsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        jobs = MLJob.objects.filter(status="success").order_by("-created_at")
        return Response(MLJobSerializer(jobs, many=True).data)
