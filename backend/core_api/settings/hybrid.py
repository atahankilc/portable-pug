import os
from .local import *

ML_INFERENCE_BACKEND = "cloud"
ML_CLOUD_URL = os.environ.get("ML_CLOUD_URL", "")
