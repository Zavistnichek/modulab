from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SpeedTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    download_speed = models.FloatField(help_text="Download speed in MB/s")
    upload_speed = models.FloatField(help_text="Upload speed in MB/s")
    ping = models.FloatField(help_text="Ping in ms")
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"Test at {self.timestamp}"
