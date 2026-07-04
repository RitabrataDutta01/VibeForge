from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):

    ROLE_CHOICES = [
            ("EMPLOYEE", 'Employee'),
            ("ADMIN", "Admin/HR")
            ]

    user = models.OneToOneField(User, on_delete= models.CASCADE)
    role = models.CharField(max_length= 10, choices= ROLE_CHOICES, default="EMPLOYEE")
    employee_id = models.CharField(max_length= 20, unique= True)
    department = models.CharField(max_length= 100, blank= True)
    job_title = models.CharField(max_length= 100, blank= True)
    phone = models.CharField(max_length= 15, blank= True)
    address = models.TextField(blank= True)
    email = models.CharField(max_length=100, blank= True)
    profile_pic = models.ImageField(upload_to= 'profile_pics/', blank= True, null= True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


DOCUMENT_TYPES = [
    ("RESUME", "Resume"),
    ("AADHAAR", "Aadhaar"),
    ("PAN", "PAN Card"),
    ("DEGREE", "Degree Certificate"),
    ("OFFER", "Offer Letter"),
    ("EXPERIENCE", "Experience Certificate"),
    ("OTHER", "Other"),
]


class EmployeeDocument(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_document_type_display()} – {self.profile.user.username}"

    @property
    def filename(self):
        return self.document.name.rsplit('/', 1)[-1]

