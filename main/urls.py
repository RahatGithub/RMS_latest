from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('semesters/<str:batch_no>/<int:semester_no>', views.semester_view, name="semester_view"),
    path('courses/<str:batch_no>/<int:semester_no>/<str:course_type>/<str:course_code>', views.course_view, name="course_view"),
    path('add_semester/<str:batch_no>', views.add_semester, name="add_semester"),
    path('delete_batch/<str:batch_no>', views.delete_batch, name="delete_batch"),
    path('delete_teacher/<str:name>', views.delete_teacher, name="delete_teacher"),
    path('students/<str:batch_no>', views.students_view, name="students_view"),
    path('teachers/<str:institute>/<str:department>/<str:name>', views.teacher_profile, name="teacher_profile"),
    path('update_course/<str:batch_no>/<int:semester_no>/<str:course_code>', views.update_course, name="update_course")
]