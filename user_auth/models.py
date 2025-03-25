from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(unique=True, error_messages={'unique': 'Email bereits vorhanden.'})
    username = models.CharField(max_length=120, default='Max Coderr')
    type = models.CharField(max_length=100, choices=[('business', 'business'), ('customer', 'customer')])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    first_name = models.CharField(max_length=80, default='Max')
    last_name = models.CharField(max_length=80, default='Coderr')
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default='Berlin')
    description = models.TextField(blank=True, max_length=1000)
    working_hours = models.CharField(max_length=100, blank=True, default='9:00 - 17:00')
    tel = models.CharField(max_length=25, blank=True, default='0123456789')
    uploaded_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        self.username = self.user.username
        if self.pk:
            original = Profile.objects.get(pk=self.pk)
            if original.file != self.file:
                self.upload_at = now()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.type}"
         