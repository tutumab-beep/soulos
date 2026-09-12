from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta, datetime
from .models import WorkLog

INDICATORS = [
    "Tx_Curr 90 days",
    "Tx Curr 28",
    "HTS TST",
    "HTS Pos",
    "HIVSS",
    "Tx_New",
    "TFI",
    "TFO",
    "Pre-ART",
    "Early Missed",
    "Late Missed",
    "Unconfirmed LTF",
    "VL Due",
    "Overall VL Done",
    "TPT Completed",
    "TPT Blanks",
    "ITS-Offered",
    "ITS-Accepted",
    "ITS-Declined",
    "Contact-Elicited",
    "Contact(s)-HIV Test",
    "Lenacapavir",
    "6MMD Review",
    "6MMD Enrolled",
    "Community TST",
    "Community Pos",
    "Community HIVSS",
]


def safe_float(v):
    try:
        return float(v) if v != "" else 0
    except (ValueError, TypeError):
        return 0


def calc_tx_curr_28(indicators_dict):
    tx_curr_90 = safe_float(indicators_dict.get("Tx_Curr 90 days", 0))
    late_missed = safe_float(indicators_dict.get("Late Missed", 0))
    return tx_curr_90 - late_missed


def parse_date(val):
    if isinstance(val, date):
        return val
    if not val:
        return date.today()
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date.today()


def get_week_range(d):
    friday = d - timedelta(days=(d.weekday() - 4) % 7)
    if friday > d:
        friday -= timedelta(days=7)
    thursday = friday + timedelta(days=6)
    return friday, thursday


def get_baseline(log, indicator):
    if not log or not log.indicators:
        return None
    return log.indicators.get(indicator)


def calculate_variance(current, baseline):
    if current is None or baseline is None:
        return None
    return current - baseline


@login_required
def dashboard(request):
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start, week_end = get_week_range(today)

    today_log = WorkLog.objects.filter(date=today).first()
    yesterday_log = WorkLog.objects.filter(date=yesterday).first()
    week_logs = WorkLog.objects.filter(date__range=(week_start, week_end)).only(
        "date", "gains", "losses", "activities", "indicators"
    )

    today_gains = today_log.gains if today_log else 0
    today_losses = today_log.losses if today_log else 0
    yesterday_gains = yesterday_log.gains if yesterday_log else 0
    yesterday_losses = yesterday_log.losses if yesterday_log else 0
    week_gains = week_logs.aggregate(total=Sum("gains"))["total"] or 0
    week_losses = week_logs.aggregate(total=Sum("losses"))["total"] or 0

    rows = []
    for indicator in INDICATORS:
        if indicator == "Tx Curr 28":
            continue
        baseline = get_baseline(yesterday_log, indicator)
        today_current = get_baseline(today_log, indicator)
        try:
            baseline = float(baseline) if baseline is not None else None
        except (ValueError, TypeError):
            baseline = None
        try:
            today_current = float(today_current) if today_current is not None else None
        except (ValueError, TypeError):
            today_current = None
        week_current = sum(
            (
                safe_float(log.indicators.get(indicator, 0) if log.indicators else 0)
                for log in week_logs
            ),
            0,
        )
        rows.append(
            {
                "indicator": indicator,
                "baseline": baseline,
                "today_current": today_current,
                "today_variance": calculate_variance(today_current, baseline),
                "week_current": week_current,
                "week_variance": calculate_variance(week_current, baseline),
            }
        )

    tx_curr_28_today = calc_tx_curr_28(
        today_log.indicators if today_log and today_log.indicators else {}
    )
    tx_curr_28_yesterday = calc_tx_curr_28(
        yesterday_log.indicators if yesterday_log and yesterday_log.indicators else {}
    )
    tx_curr_28_week = sum(
        calc_tx_curr_28(log.indicators if log.indicators else {}) for log in week_logs
    )
    tx_curr_28_row = {
        "indicator": "Tx Curr 28",
        "baseline": tx_curr_28_yesterday,
        "today_current": tx_curr_28_today,
        "today_variance": calculate_variance(tx_curr_28_today, tx_curr_28_yesterday),
        "week_current": tx_curr_28_week,
        "week_variance": None,
    }
    for i, row in enumerate(rows):
        if row["indicator"] == "Tx_Curr 90 days":
            rows.insert(i + 1, tx_curr_28_row)
            break

    context = {
        "today": today,
        "yesterday": yesterday,
        "week_start": week_start,
        "week_end": week_end,
        "today_facility": today_log.facility if today_log else "",
        "yesterday_facility": yesterday_log.facility if yesterday_log else "",
        "today_gains": today_gains,
        "today_losses": today_losses,
        "today_net": today_gains - today_losses,
        "yesterday_gains": yesterday_gains,
        "yesterday_losses": yesterday_losses,
        "yesterday_net": yesterday_gains - yesterday_losses,
        "week_gains": week_gains,
        "week_losses": week_losses,
        "week_net": week_gains - week_losses,
        "rows": rows,
    }
    return render(request, "system_apps/work_alignment/dashboard.html", context)


@login_required
def edit_entry(request, entry_date=None):
    if request.GET.get("entry_date"):
        target_date = parse_date(request.GET.get("entry_date"))
        return redirect("work_alignment:edit_entry_date", entry_date=target_date)
    target_date = parse_date(entry_date)
    log = WorkLog.objects.filter(date=target_date).first()
    if request.method == "POST":

        def to_num(v):
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0

        data = {
            "date": target_date,
            "facility": request.POST.get("facility", ""),
            "activities": request.POST.get("activities", ""),
            "meetings": request.POST.get("meetings", ""),
            "outcomes": request.POST.get("outcomes", ""),
            "challenges": request.POST.get("challenges", ""),
            "solutions": request.POST.get("solutions", ""),
            "daily_plan": request.POST.get("daily_plan", ""),
            "achievements": request.POST.get("achievements", ""),
            "failures": request.POST.get("failures", ""),
            "gains": int(request.POST.get("gains", 0)),
            "losses": int(request.POST.get("losses", 0)),
            "indicators": {
                ind: to_num(request.POST.get(f"current_{ind}", ""))
                for ind in INDICATORS
                if ind != "Tx Curr 28"
            },
            "indicators_baseline": {
                ind: to_num(request.POST.get(f"baseline_{ind}", ""))
                for ind in INDICATORS
                if ind != "Tx Curr 28"
            },
        }
        data["indicators"]["Tx Curr 28"] = calc_tx_curr_28(data["indicators"])
        tx_curr_90_baseline = to_num(request.POST.get("baseline_Tx_Curr 90 days", ""))
        late_missed_baseline = to_num(request.POST.get("baseline_Late Missed", ""))
        data["indicators_baseline"]["Tx Curr 28"] = (
            tx_curr_90_baseline - late_missed_baseline
        )
        if log:
            for k, v in data.items():
                setattr(log, k, v)
            log.save()
        else:
            WorkLog.objects.create(**data)
        return redirect("work_alignment:dashboard")
    indicators_list = []
    yesterday_log = WorkLog.objects.filter(date=target_date - timedelta(days=1)).first()
    yesterday_indicators = (
        yesterday_log.indicators if yesterday_log and yesterday_log.indicators else {}
    )
    current_indicators = log.indicators if log and log.indicators else {}
    for ind in INDICATORS:
        if ind == "Tx Curr 28":
            continue
        baseline = yesterday_indicators.get(ind, 0)
        current = current_indicators.get(ind, 0)
        try:
            baseline_val = float(baseline) if baseline != "" else 0
        except (ValueError, TypeError):
            baseline_val = 0
        try:
            current_val = float(current) if current != "" else 0
        except (ValueError, TypeError):
            current_val = 0
        indicators_list.append(
            {
                "name": ind,
                "baseline": baseline_val,
                "current": current_val,
                "variance": current_val - baseline_val,
            }
        )
    tx_curr_28_current = calc_tx_curr_28(current_indicators)
    tx_curr_28_baseline = calc_tx_curr_28(yesterday_indicators)
    indicators_list.append(
        {
            "name": "Tx Curr 28",
            "baseline": tx_curr_28_baseline,
            "current": tx_curr_28_current,
            "variance": tx_curr_28_current - tx_curr_28_baseline,
        }
    )
    context = {
        "log": log,
        "target_date": target_date,
        "indicators": indicators_list,
        "yesterday": target_date - timedelta(days=1),
    }
    return render(request, "system_apps/work_alignment/edit_entry.html", context)


@login_required
def entries(request):
    logs = (
        WorkLog.objects.all()
        .only("date", "gains", "losses", "activities")
        .order_by("-date")
    )
    return render(
        request,
        "system_apps/work_alignment/entries.html",
        {"logs": logs},
    )


@login_required
def weekly_view(request):
    today = date.today()
    week_start, week_end = get_week_range(today)
    logs = WorkLog.objects.filter(date__range=(week_start, week_end)).order_by("date")
    return render(
        request,
        "system_apps/work_alignment/weekly.html",
        {
            "logs": [
                {
                    "date": log.date,
                    "gains": log.gains,
                    "losses": log.losses,
                    "net": log.gains - log.losses,
                    "activities": log.activities,
                }
                for log in logs
            ],
            "week_start": week_start,
            "week_end": week_end,
        },
    )


@login_required
def monthly_view(request):
    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(
            days=1
        )
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    logs = WorkLog.objects.filter(date__range=(month_start, month_end)).order_by("date")
    return render(
        request,
        "system_apps/work_alignment/monthly.html",
        {
            "logs": [
                {
                    "date": log.date,
                    "gains": log.gains,
                    "losses": log.losses,
                    "net": log.gains - log.losses,
                }
                for log in logs
            ],
            "month_start": month_start,
            "month_end": month_end,
        },
    )
