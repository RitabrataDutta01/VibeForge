from django.db import models
from django.contrib.auth.models import User


class SalaryStructure(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_structure')
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    @property
    def net_salary(self):
        return self.base_salary + self.allowances - self.deductions

    def __str__(self):
        return f"Salary Structure - {self.user.username} (Net: {self.net_salary})"


class Payslip(models.Model):
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payslips')
    month = models.IntegerField()
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2)
    deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    paid_date = models.DateField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"Payslip - {self.user.username} - {self.month}/{self.year} ({self.status})"
