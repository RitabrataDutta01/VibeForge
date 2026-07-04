from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import TextInput, PasswordInput
from . models import Profile, EmployeeDocument
class SignupForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField(widget=forms.EmailInput)
    employee_id = forms.CharField(max_length= 20)
    role = forms.ChoiceField(choices= Profile.ROLE_CHOICES)


    class Meta:

        model = User
        fields = ['username', 'email', 'password']

MAX_PROFILE_PIC_MB = 2
ALLOWED_PROFILE_PIC_TYPES = ['image/jpeg', 'image/png', 'image/webp']


def validate_profile_pic(pic):
    if not pic:
        return pic
    if pic.size > MAX_PROFILE_PIC_MB * 1024 * 1024:
        raise forms.ValidationError(f"Image must be smaller than {MAX_PROFILE_PIC_MB}MB.")
    content_type = getattr(pic, 'content_type', None)
    if content_type and content_type not in ALLOWED_PROFILE_PIC_TYPES:
        raise forms.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
    return pic


class EmployeeProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['address', 'phone', 'profile_pic'] 

    def clean_profile_pic(self):
        return validate_profile_pic(self.cleaned_data.get('profile_pic'))

        
class AdminProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['department', 'job_title', 'address', 'phone', 'profile_pic']               

    def clean_profile_pic(self):
        return validate_profile_pic(self.cleaned_data.get('profile_pic'))


MAX_DOCUMENT_MB = 5
ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]


class EmployeeDocumentForm(forms.ModelForm):

    class Meta:
        model = EmployeeDocument
        fields = ['document_type', 'document']

    def clean_document(self):
        doc = self.cleaned_data.get('document')
        if not doc:
            raise forms.ValidationError("Please choose a file to upload.")
        if doc.size > MAX_DOCUMENT_MB * 1024 * 1024:
            raise forms.ValidationError(f"File must be smaller than {MAX_DOCUMENT_MB}MB.")
        content_type = getattr(doc, 'content_type', None)
        if content_type and content_type not in ALLOWED_DOCUMENT_TYPES:
            raise forms.ValidationError("Only PDF, Word, or image files are allowed.")
        return doc


class UserInfoForm(forms.ModelForm):
    """Lets a logged-in user update their own basic account info."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(),
            'last_name': forms.TextInput(),
            'email': forms.EmailInput(),
        }
        


