from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('semesters/<str:batch_no>/<int:semester_no>', views.semester_view, name="semester_view"),
    path('courses/<str:batch_no>/<int:semester_no>/<str:course_type>/<str:course_code>', views.course_view, name="course_view"),
    path('add_semester/<str:batch_no>', views.add_semester, name="add_semester"),
]