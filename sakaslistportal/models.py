from django.db import models

from django.contrib.auth.models import User

# Department model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="categories")

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# Staff Profile (One-to-One with User)
class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    # Round-robin load tracking (last assigned time)
    last_assigned = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.department}"


STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
]

class Query(models.Model):
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    title = models.CharField(max_length=200, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="queries")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_queries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #Auto-generated ticket number

    query_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.query_number:
            last_id = Query.objects.all().count() + 1
            self.query_number = f"QRY-{last_id:05d}"  # QRY-00001 format
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.query_number} - {self.department.name} ({self.status})"


class Resolution(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="resolutions")
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resolution for Query #{self.query.id} by {self.staff.username}"