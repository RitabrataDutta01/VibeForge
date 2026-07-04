from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import TextInput, PasswordInput
from . models import Profile

class SignupForm(UserCreationForm):
    
    password = forms.CharField(widget= forms.PasswordInput)
    email = forms.CharField(widget=forms.EmailInput)
    employee_id = forms.CharField(max_length= 20)
    role = forms.ChoiceField(choices= Profile.ROLE_CHOICES)
    
    
    class Meta:
        
        model = User
        fields = ['username', 'email', 'password']

class EmployeeProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['address', 'phone', 'profile_pic'] 
        
class AdminProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['department', 'job_title', 'address', 'phone', 'profile_pic']               