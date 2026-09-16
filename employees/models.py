from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    joining_date = models.DateField()

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"


class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type}"