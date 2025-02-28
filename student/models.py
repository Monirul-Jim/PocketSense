from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='custom_groups')

    def __str__(self):
        return self.name


class Expense(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expenses_paid')
    created_at = models.DateTimeField(auto_now_add=True)
    split_among = models.ManyToManyField(User, related_name='expenses_shared')

    def __str__(self):
        return f"{self.description} - {self.amount}"
