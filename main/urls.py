from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('semesters/<str:batch_no>/<int:semester_no>',
         views.semester_view, name="semester_view"),
    path('courses/<str:batch_no>/<int:semester_no>/<str:course_type>/<str:course_code>',
         views.course_view, name="course_view"),
    path('add_semester/<str:batch_no>', views.add_semester, name="add_semester"),
    path('delete_batch/<str:batch_no>', views.delete_batch, name="delete_batch"),
    path('delete_teacher/<str:name>', views.delete_teacher, name="delete_teacher"),
    path('delete_student/<str:batch_no>/<str:reg_no>',
         views.delete_student, name="delete_student"),
    path('students/<str:batch_no>', views.students_view, name="students_view"),
    path('teachers/<str:institute>/<str:department>/<str:name>',
         views.teacher_profile, name="teacher_profile"),
    path('update_course/<str:batch_no>/<int:semester_no>/<str:course_code>',
         views.update_course, name="update_course"),
    path('update_student/<str:batch_no>/<str:reg_no>',
         views.update_student, name="update_student"),

    # testing of assessment calculation
    path('assessments/<str:batch_no>/<int:semester_no>/<str:course_code>',
         views.assessments, name="assessments"),
    path('assessments/<str:batch_no>/<int:semester_no>/<str:course_code>/overall_assessment',
         views.overall_assessment, name="overall_assessment"),
    path('assessments/<str:batch_no>/<int:semester_no>/<str:course_code>/attendance',
         views.add_attendance, name="add_attendance"),

    path('gradesheet_view/<str:reg_no>',
         views.gradesheet_view, name="gradesheet_view")
]
