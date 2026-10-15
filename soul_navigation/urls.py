from django.urls import path
from . import views

app_name = "soul_navigation"

urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.start_navigation, name="start"),
    path("step/1/<int:session_id>/", views.step_observe, name="step_observe"),
    path("step/2/<int:session_id>/", views.step_understand, name="step_understand"),
    path("step/3/<int:session_id>/", views.step_examine, name="step_examine"),
    path("step/4/<int:session_id>/", views.step_reframe, name="step_reframe"),
    path("step/5/<int:session_id>/", views.step_move, name="step_move"),
    path("step/6/<int:session_id>/", views.step_integrate, name="step_integrate"),
    path("summary/<int:session_id>/", views.summary, name="summary"),
    path("checkin/", views.daily_checkin, name="daily_checkin"),
    path("history/", views.history, name="history"),
    path("save/", views.save_session, name="save_session"),
    path("export/<int:session_id>/", views.export_session, name="export_session"),
]
