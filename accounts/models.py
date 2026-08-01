from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    pass  # You can add custom fields here later

    def __str__(self):
        return self.username