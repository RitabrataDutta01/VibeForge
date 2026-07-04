from django import forms
from .models import SalaryStructure


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ('base_salary', 'allowances', 'deductions')
        widgets = {
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
