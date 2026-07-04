from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LeaveRequest
from attendance.models import Attendance


@login_required
def leave_home(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        leave_type = request.POST.get("leave_type")
        remarks = request.POST.get("remarks", "")

        if not start_date or not end_date or not leave_type:
            messages.error(request, "Please fill in leave type and both dates.")
        elif start_date > end_date:
            messages.error(request, "Start date cannot be after end date.")
        else:
            LeaveRequest.objects.create(
                employee=request.user,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                remarks=remarks,
            )
            messages.success(request, "Leave request submitted.")
        return redirect("leaves:home")

    my_requests = LeaveRequest.objects.filter(employee=request.user)
    counts = {
        "pending": my_requests.filter(status="Pending").count(),
        "approved": my_requests.filter(status="Approved").count(),
        "rejected": my_requests.filter(status="Rejected").count(),
    }
    return render(request, "leaves/leave_home.html", {"requests": my_requests, "counts": counts})


@login_required
def leave_admin_list(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'):
        messages.error(request, "You don't have access to this page.")
        return redirect("leaves:home")

    status_filter = request.GET.get("status", "Pending")
    if status_filter:
        requests_qs = LeaveRequest.objects.filter(status=status_filter)
    else:
        requests_qs = LeaveRequest.objects.all()

    return render(request, "leaves/leave_admin.html", {
        "requests": requests_qs, "status_filter": status_filter
    })


@login_required
def leave_decide(request, leave_id, decision):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'):
        messages.error(request, "You don't have access to this page.")
        return redirect("leaves:home")

    leave = get_object_or_404(LeaveRequest, id=leave_id)
    if decision not in ("Approved", "Rejected"):
        messages.error(request, "Invalid decision.")
        return redirect("leaves:admin_list")

    leave.status = decision
    leave.comment = request.POST.get("comment", "")
    leave.save()

    if decision == "Approved":
        d = leave.start_date
        while d <= leave.end_date:
            Attendance.objects.update_or_create(
                employee=leave.employee, date=d,
                defaults={"status": "Leave"}
            )
            d += timedelta(days=1)

    messages.success(request, f"Leave request {decision.lower()}.")
    return redirect("leaves:admin_list")