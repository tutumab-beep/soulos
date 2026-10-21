from django import template
from django.contrib.auth.models import AnonymousUser
from ..models import UserProgress

register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_progress(context, module_name):
    """Get user progress for a specific module"""
    request = context.get("request")
    if (
        not request
        or hasattr(request, "user")
        and isinstance(request.user, AnonymousUser)
    ):
        return None

    if not request.user.is_authenticated:
        return None

    try:
        return UserProgress.objects.get(
            user=request.user, module_name=module_name, is_active=True
        )
    except UserProgress.DoesNotExist:
        return None


@register.inclusion_tag("soul_anticipate/resume_dialog.html", takes_context=True)
def show_resume_dialog(context, module_name, module_display_name):
    """Show resume dialog if user has progress in this module"""
    request = context.get("request")
    if (
        not request
        or hasattr(request, "user")
        and isinstance(request.user, AnonymousUser)
    ):
        return {"show_dialog": False}

    if not request.user.is_authenticated:
        return {"show_dialog": False}

    # Check if we've already shown a resume dialog in this session
    # to prevent showing it on every page load
    if request.session.get("resume_dialog_shown", False):
        return {"show_dialog": False}

    try:
        progress = UserProgress.objects.get(
            user=request.user, module_name=module_name, is_active=True
        )

        # Only show dialog if there's meaningful progress
        if progress.completion_status in ["not_started", "completed"]:
            return {"show_dialog": False}

        # Mark that we've shown a resume dialog in this session
        request.session["resume_dialog_shown"] = True

        return {
            "show_dialog": True,
            "progress": progress,
            "module_display_name": module_display_name,
        }
    except UserProgress.DoesNotExist:
        return {"show_dialog": False}


@register.simple_tag
def resume_url(module_name):
    """Get URL to resume a module"""
    # This would typically map to a resume view for each module
    # For now, we'll return the module's main URL
    url_mapping = {
        "core_healing_path": "core_healing_path:dashboard",
        "soul_navigation": "soul_navigation:home",
        "daily_alignment": "daily_alignment:dashboard",
        "soul_anticipate": "soul_anticipate:dashboard",
        "soullog": "soullog:journal",
        "soulconnect": "soulconnect:dashboard",
        "work_alignment": "work_alignment:dashboard",
        "ego_balance": "ego_balance:dashboard",
    }

    return url_mapping.get(module_name, "#")
