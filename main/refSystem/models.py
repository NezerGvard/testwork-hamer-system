from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=12, verbose_name='номер телефона')
    status = models.BooleanField(blank=True, default=False)
    
    def __str__(self) -> str:
        return self.username


class Code(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='нормер пользователя')
    code = models.CharField(max_length=4, verbose_name="код подтверждения")

    def __str__(self) -> str:
        return self.user.phone_number + " " +  self.code


class ReferralCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='нормер пользователя')
    self_code = models.CharField(max_length=6, verbose_name="код пользователя")
    activate_code = models.CharField(max_length=6, verbose_name="активированный код", blank=True)
    activate_user = models.ManyToManyField(CustomUser, verbose_name="ваши рефералы", blank=True, related_name='+')
    
    def __str__(self) -> str:
        return self.user.username + " " +  self.self_code

