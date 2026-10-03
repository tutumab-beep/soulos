from django.contrib import admin
from .models import (
    DailyPlan,
    Priority,
    DailyTask,
    Ritual,
    RitualCompletion,
    DailyReflection,
)

admin.site.register(DailyPlan)
admin.site.register(Priority)
admin.site.register(DailyTask)
admin.site.register(Ritual)
admin.site.register(RitualCompletion)
admin.site.register(DailyReflection)
