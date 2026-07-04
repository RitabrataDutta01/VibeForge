from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

from .models import SalaryStructure, Payslip
from .forms import SalaryStructureForm
from accounts.views import isAdmin
from accounts.models import Profile


@login_required
def employee_payroll_view(request):
    structure = SalaryStructure.objects.filter(user=request.user).first()
    payslips = Payslip.objects.filter(user=request.user).order_by('-year', '-month')

    context = {
        'structure': structure,
        'payslips': payslips,
    }
    return render(request, 'payroll/employee_payroll.html', context)


@login_required
@user_passes_test(isAdmin)
def admin_payroll_view(request):
    profiles = (
        Profile.objects.exclude(user=request.user)
        .select_related('user', 'user__salary_structure')
        .order_by('employee_id')
    )
    payslips = (
        Payslip.objects.all()
        .select_related('user', 'user__profile')
        .order_by('-year', '-month', '-generated_at')
    )

    today = timezone.localdate()

    context = {
        'profiles': profiles,
        'payslips': payslips,
        'current_month': today.month,
        'current_year': today.year,
    }
    return render(request, 'payroll/admin_payroll.html', context)


@login_required
@user_passes_test(isAdmin)
def admin_update_salary(request, employee_id):
    profile = get_object_or_404(Profile, employee_id=employee_id)
    employee = profile.user
    structure, created = SalaryStructure.objects.get_or_create(user=employee)

    if request.method == 'POST':
        form = SalaryStructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, f"Salary structure for {employee.username} updated successfully.")
            return redirect('payroll:admin_payroll')
    else:
        form = SalaryStructureForm(instance=structure)

    return render(request, 'payroll/admin_update_salary.html', {'form': form, 'profile': profile})


@login_required
@user_passes_test(isAdmin)
def admin_generate_payslip_view(request):
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
        except (ValueError, TypeError):
            messages.error(request, "Invalid month or year selected.")
            return redirect('payroll:admin_payroll')

        profiles = Profile.objects.exclude(role='ADMIN')
        generated_count = 0
        skipped_count = 0

        for profile in profiles:
            emp = profile.user
            structure = SalaryStructure.objects.filter(user=emp).first()
            if not structure:
                structure = SalaryStructure.objects.create(user=emp)

            exists = Payslip.objects.filter(user=emp, month=month, year=year).exists()
            if not exists:
                Payslip.objects.create(
                    user=emp,
                    month=month,
                    year=year,
                    base_salary=structure.base_salary,
                    allowances=structure.allowances,
                    deductions=structure.deductions,
                    net_salary=structure.net_salary,
                    status='unpaid'
                )
                generated_count += 1
            else:
                skipped_count += 1

        messages.success(
            request,
            f"Payslip generation completed. Generated: {generated_count}, Skipped (already existed): {skipped_count}."
        )
    return redirect('payroll:admin_payroll')


@login_required
@user_passes_test(isAdmin)
def admin_pay_payslip_view(request, payslip_id):
    payslip = get_object_or_404(Payslip, id=payslip_id)
    if payslip.status == 'unpaid':
        payslip.status = 'paid'
        payslip.paid_date = timezone.localdate()
        payslip.save()
        messages.success(request, f"Payslip for {payslip.user.username} (Month: {payslip.month}/{payslip.year}) marked as Paid.")
    return redirect('payroll:admin_payroll')
