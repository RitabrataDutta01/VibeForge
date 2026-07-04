from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import SignupForm, EmployeeProfileForm, AdminProfileForm, UserInfoForm
from .models import Profile
from django.contrib import messages
import json
from .services.gemini import ask_gemini
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from payroll.models import SalaryStructure, Payslip
from attendance.models import Attendance
from leaves.models import LeaveRequest
from django.utils import timezone


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
    today = timezone.localdate()
    context = {'profile': profile, 'today': today}

    if is_admin:
        template = 'accounts/admin_dashboard.html'

        employee_profiles = Profile.objects.filter(role='EMPLOYEE')
        total_employees = employee_profiles.count()

        today_attendance = Attendance.objects.filter(
            employee__profile__role='EMPLOYEE', date=today
        )
        present_today = today_attendance.filter(status='Present').count()
        half_day_today = today_attendance.filter(status='Half-day').count()
        leave_today = today_attendance.filter(status='Leave').count()
        absent_today = max(total_employees - (present_today + half_day_today + leave_today), 0)

        pending_leaves = LeaveRequest.objects.filter(status='Pending').order_by('applied_at')
        pending_leaves_count = pending_leaves.count()

        unpaid_payslips = Payslip.objects.filter(status='unpaid').count()
        payslips_this_month = Payslip.objects.filter(month=today.month, year=today.year).count()

        context.update({
            'total_employees': total_employees,
            'present_today': present_today,
            'half_day_today': half_day_today,
            'leave_today': leave_today,
            'absent_today': absent_today,
            'pending_leaves_count': pending_leaves_count,
            'recent_pending_leaves': pending_leaves[:5],
            'unpaid_payslips': unpaid_payslips,
            'payslips_this_month': payslips_this_month,
        })
    else:
        template = 'accounts/employee_dashboard.html'

        attendance_today = Attendance.objects.filter(employee=request.user, date=today).first()

        my_leaves = LeaveRequest.objects.filter(employee=request.user)
        leave_counts = {
            'pending': my_leaves.filter(status='Pending').count(),
            'approved': my_leaves.filter(status='Approved').count(),
            'rejected': my_leaves.filter(status='Rejected').count(),
        }

        structure = SalaryStructure.objects.filter(user=request.user).first()
        latest_payslip = Payslip.objects.filter(user=request.user).order_by('-year', '-month').first()

        context.update({
            'attendance_today': attendance_today,
            'leave_counts': leave_counts,
            'recent_leaves': my_leaves[:3],
            'structure': structure,
            'latest_payslip': latest_payslip,
        })

    return render(request, template, context)

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

@login_required
def settings_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = EmployeeProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('settings')
        else:
            messages.error(request, "Please fix the errors below and try again.")
    else:
        user_form = UserInfoForm(instance=request.user)
        profile_form = EmployeeProfileForm(instance=profile)

    return render(request, 'accounts/settings.html', {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@user_passes_test(isAdmin)
def employee_records_view(request):
    
    query_id = request.GET.get('employee_id', '').strip()
    target_profile = None
    attendance_records = None
    leave_records = None
    attendance_summary = None
    leave_summary = None
    error = None

    if query_id:
        target_profile = Profile.objects.select_related('user').filter(employee_id__iexact=query_id).first()
        if not target_profile:
            error = f"No employee found with ID \"{query_id}\"."
        else:
            emp_user = target_profile.user
            all_attendance = Attendance.objects.filter(employee=emp_user)
            attendance_records = all_attendance.order_by('-date')[:90]
            attendance_summary = {
                'present': all_attendance.filter(status='Present').count(),
                'absent': all_attendance.filter(status='Absent').count(),
                'half_day': all_attendance.filter(status='Half-day').count(),
                'leave': all_attendance.filter(status='Leave').count(),
                'total': all_attendance.count(),
            }

            all_leaves = LeaveRequest.objects.filter(employee=emp_user)
            leave_records = all_leaves
            leave_summary = {
                'pending': all_leaves.filter(status='Pending').count(),
                'approved': all_leaves.filter(status='Approved').count(),
                'rejected': all_leaves.filter(status='Rejected').count(),
                'total': all_leaves.count(),
            }

    return render(request, 'accounts/employee_records.html', {
        'query_id': query_id,
        'target_profile': target_profile,
        'attendance_records': attendance_records,
        'leave_records': leave_records,
        'attendance_summary': attendance_summary,
        'leave_summary': leave_summary,
        'error': error,
    })


@login_required
@require_POST
def chatbot_reply_view(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    try:
        reply = ask_gemini(message)
    except Exception:
        reply = "Sorry, I'm having trouble reaching the assistant right now. Please try again."

    return JsonResponse({'reply': reply})


@login_required
def upload_document(request):
    if request.method == "POST":
        form = EmployeeDocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            document = form.save(commit=False)
            document.profile = request.user.profile
            document.save()

            return redirect("profile")

    else:
        form = EmployeeDocumentForm()

    return render(
        request,
        "accounts/upload_document.html",
        {
            "form": form
        }
    )
    
