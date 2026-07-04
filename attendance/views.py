import calendar as calendar_module
from datetime import date
from collections import Counter
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Attendance


@login_required
def attendance_home(request):
    today = timezone.localdate()
    record, _ = Attendance.objects.get_or_create(
        employee=request.user, date=today,
        defaults={"status": "Absent"}
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "checkin":
            if record.check_in:
                messages.error(request, "You've already checked in today.")
            else:
                record.check_in = timezone.now()
                record.status = "Present"
                record.save()
                messages.success(request, "Checked in successfully.")
        elif action == "checkout":
            if not record.check_in:
                messages.error(request, "Check in first before checking out.")
            elif record.check_out:
                messages.error(request, "You've already checked out today.")
            else:
                record.check_out = timezone.now()
                hours = (record.check_out - record.check_in).total_seconds() / 3600
                if hours < 4:
                    record.status = "Half-day"
                record.save()
                messages.success(request, "Checked out successfully.")
        return redirect("attendance:home")

    # Build current month's calendar data
    month_str = request.GET.get("month", today.strftime("%Y-%m"))
    year, month = map(int, month_str.split("-"))
    month_records = Attendance.objects.filter(
        employee=request.user, date__year=year, date__month=month
    )
    records_by_day = {r.date.day: r for r in month_records}

    cal = calendar_module.Calendar(firstweekday=6)  # weeks start on Sunday
    calendar_days = []
    for d in cal.itermonthdates(year, month):
        in_month = d.month == month and d.year == year
        rec = records_by_day.get(d.day) if in_month else None
        calendar_days.append({
            "date": d,
            "day": d.day,
            "in_month": in_month,
            "status": rec.status if rec else None,
            "is_today": d == today,
        })

    context = {
        "record": record,
        "calendar_days": calendar_days,
        "year": year,
        "month": month,
        "month_str": month_str,
        "today": today,
    }
    return render(request, "attendance/attendance_home.html", context)


@login_required
def attendance_admin_roster(request):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to this page.")
        return redirect("attendance:home")

    selected_date = request.GET.get("date", timezone.localdate().isoformat())
    d = date.fromisoformat(selected_date)

    employees = User.objects.filter(is_staff=False)
    roster = []
    for emp in employees:
        record = Attendance.objects.filter(employee=emp, date=d).first()
        roster.append({
            "employee": emp,
            "status": record.status if record else "Absent",
            "check_in": record.check_in if record else None,
            "check_out": record.check_out if record else None,
        })

    counts = Counter(row["status"] for row in roster)

    return render(request, "attendance/attendance_admin.html", {
        "roster": roster, "selected_date": selected_date, "counts": counts
    })