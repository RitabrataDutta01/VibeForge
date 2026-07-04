from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import SignupForm, EmployeeProfileForm, AdminProfileForm
from .models import Profile
from django.contrib import messages

# Create your views here.

def isAdmin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'


@login_required
@user_passes_test(isAdmin)
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            Profile.objects.create(
                user=user,
                role='EMPLOYEE',
                employee_id=form.cleaned_data['employee_id'],
            )
            messages.success(request, f"Account created successfully for {user.username}.")
            return redirect('employee_list')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user:
            login(request, user)
            return redirect('profile')
        return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html') 

@login_required
def profile_view(request):
    profile = request.user.profile
    is_admin = profile.role == 'ADMIN'
    FormClass = AdminProfileForm if is_admin else EmployeeProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = FormClass(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

def logout_view(request):
    logout(request)
    return redirect('login')

# accounts/views.py
@login_required
@user_passes_test(isAdmin)
def employee_list_view(request):
    profiles = Profile.objects.exclude(user=request.user).select_related('user')
    return render(request, 'accounts/employee_list.html', {'profiles': profiles})


@login_required
@user_passes_test(isAdmin)
def edit_employee_view(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = AdminProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})