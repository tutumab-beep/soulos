import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import UserProgress


class ProgressTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically track and save user progress across modules
    """

    def process_request(self, request):
        # Store the current path in session for comparison later
        if hasattr(request, "user") and not isinstance(request.user, AnonymousUser):
            request.session["last_visited_path"] = request.path
            request.session["last_visited_time"] = str(timezone.now())
        return None

    def process_response(self, request, response):
        # Save progress when user navigates away or session ends
        if (
            hasattr(request, "user")
            and not isinstance(request.user, AnonymousUser)
            and request.user.is_authenticated
        ):
            self._save_user_progress(request)

        return response

    def _save_user_progress(self, request):
        """Save or update user progress based on current request"""
        try:
            # Extract module name from path
            module_name = self._extract_module_name(request.path)

            # Skip if not a trackable module
            if not self._is_trackable_module(module_name):
                return

            # Get or create progress record
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                module_name=module_name,
                defaults={"is_active": True, "completion_status": "in_progress"},
            )

            # Prepare progress data
            progress_data = {
                "current_page": request.path,
                "current_step": request.GET.get("step", ""),
                "current_substep": request.GET.get("substep", ""),
                "current_tab": request.GET.get("tab", ""),
                "entered_data": self._extract_form_data(request),
                "timestamp": timezone.now(),
            }

            # Update completion status based on URL patterns
            progress_data["completion_status"] = self._determine_completion_status(
                request.path, progress_data["current_step"]
            )

            # Save progress
            progress.save_progress(**progress_data)

        except Exception as e:
            # Log error but don't break the user experience
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error saving user progress: {e}")

    def _extract_module_name(self, path):
        """Extract module name from URL path"""
        # Remove leading/trailing slashes and split
        parts = [part for part in path.strip("/").split("/") if part]

        # Map URLs to module names
        module_mapping = {
            "core-healing-path": "core_healing_path",
            "soul-navigation": "soul_navigation",
            "daily-alignment": "daily_alignment",
            "soul-anticipate": "soul_anticipate",
            "soullog": "soullog",
            "soulconnect": "soulconnect",
            "work-alignment": "work_alignment",
            "ego-balance": "ego_balance",
        }

        if parts and parts[0] in module_mapping:
            return module_mapping[parts[0]]

        # Default to first part if not in mapping
        return parts[0] if parts else "unknown"

    def _is_trackable_module(self, module_name):
        """Check if module should be tracked for resume functionality"""
        trackable_modules = [
            "core_healing_path",
            "soul_navigation",
            "daily_alignment",
            "soul_anticipate",
            "soullog",
            "soulconnect",
            "work_alignment",
            "ego_balance",
        ]
        return module_name in trackable_modules

    def _extract_form_data(self, request):
        """Extract form data from request for saving"""
        form_data = {}

        # Get POST data
        if request.method == "POST":
            for key, value in request.POST.items():
                # Skip CSRF token and other non-essential fields
                if key not in ["csrfmiddlewaretoken"]:
                    form_data[key] = value

        # Get FILES data if needed
        if hasattr(request, "FILES"):
            for key, file in request.FILES.items():
                form_data[f"{key}_filename"] = file.name

        return form_data

    def _determine_completion_status(self, path, current_step):
        """Determine completion status based on URL and step"""
        # Check for completion patterns in URL
        if any(pattern in path.lower() for pattern in ["complete", "finished", "done"]):
            return "completed"

        # Check if step indicates completion
        if current_step and any(
            pattern in current_step.lower()
            for pattern in ["complete", "finish", "done"]
        ):
            return "completed"

        # Default to in progress
        return "in_progress"
