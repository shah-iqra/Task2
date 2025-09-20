from django.contrib import admin
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Employee, Task

# Inline Task inside Employee admin
class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ('title', 'description', 'due_date', 'status')
    readonly_fields = ('days_left',)

    def days_left(self, obj):
        delta = obj.due_date - timezone.now().date()
        return delta.days
    days_left.short_description = 'Days Left'

# Employee Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'joining_date')
    search_fields = ('name', 'email')
    inlines = [TaskInline]

# Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_employee', 'status', 'days_left')
    search_fields = ('title',)
    list_filter = ('status', 'assigned_employee')

    def days_left(self, obj):
        delta = obj.due_date - timezone.now().date()
        return delta.days
    days_left.short_description = 'Days Left'

    # Fixed indentation here
    def save_model(self, request, obj, form, change):
        if obj.status == 'Pending':
            pending_tasks = Task.objects.filter(
                assigned_employee=obj.assigned_employee,
                status='Pending'
            )
            if obj.pk:
                pending_tasks = pending_tasks.exclude(pk=obj.pk)
            if pending_tasks.count() >= 5:
                raise ValidationError(
                    f"{obj.assigned_employee.name} already has 5 pending tasks."
                )
        super().save_model(request, obj, form, change)
