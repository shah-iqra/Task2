from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Employee model
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    joining_date = models.DateField()

    def __str__(self):
        return self.name

# Task status choices
STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
]

# Task model
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

    # Validation: Prevent assigning more than 5 pending tasks
    def clean(self):
        if self.status == 'Pending':
            pending_tasks = Task.objects.filter(assigned_employee=self.assigned_employee, status='Pending')
            if self.pk:  # Exclude current task if editing
                pending_tasks = pending_tasks.exclude(pk=self.pk)
            if pending_tasks.count() >= 5:
                raise ValidationError(f"{self.assigned_employee.name} already has 5 pending tasks.")

    # Calculated field: days left until due date
    @property
    def days_left(self):
        delta = self.due_date - timezone.now().date()
        return delta.days
