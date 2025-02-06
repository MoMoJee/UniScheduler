from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# class UserData(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     key = models.CharField(max_length=100)
#     value = models.TextField()
#
#     def __str__(self):
#         return f"{self.user.username} - {self.key}"