from math import ceil
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from .models import Batch, Semester, Course, Student, TheoryCourseResult, SessionalCourseResult, Result, Teacher, AssessmentResult
from .forms import UpdateCourse, UpdateStudent
import json
from random import randint


# this is the dashboard
def dashboard(request):
    if request.method == "POST":  # when submitting the 'add batch' form
        if request.POST['form_name'] == 'add_batch_form':
            batch_no = request.POST['batch_no']
            session = request.POST['session']
            batch = Batch.objects.create(batch_no=batch_no, session=session)
            batches = Batch.objects.all()
            teachers = Teacher.objects.all()
            return render(request, 'main/dashboard.html', {'batches': batches, 'teachers': teachers})
        elif request.POST['form_name'] == 'add_teacher_form':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            name = first_name + ' ' + last_name
            email = request.POST['email']
            phone = request.POST['phone']
            designation = request.POST['designation']
            department = request.POST['department']
            institute = request.POST['institute']

            # Generating a username for the teacher:
            username = (name.replace(" ", "")).lower()[
                :5] + '_' + str(randint(100, 999))

            # Generating a code/password for the teacher:
            password = chr(randint(97, 122)) + chr(randint(97, 122)) + chr(randint(97, 122)) + chr(
                randint(48, 57)) + chr(randint(48, 57)) + chr(randint(48, 57)) + chr(randint(35, 38))

            Teacher.objects.create(name=name, email=email, phone=phone,
                                   designation=designation, department=department, institute=institute)
            user = User.objects.create_user(username, email, password)
            user.first_name, user.last_name = first_name, last_name
            user.save()
            teachers = Teacher.objects.all()
            batches = Batch.objects.all()

            new_teacher_info = {
                'username': username,
                'password': password,
                'email': email
            }
            return render(request, 'main/dashboard.html', {'batches': batches, 'teachers': teachers, 'new_teacher_info': new_teacher_info})
        elif request.POST['form_name'] == 'gradesheet_generator_form':
            reg_no = request.POST['reg_no']
            try:
                student = Student.objects.get(reg_no=reg_no)
                session = student.session
                return redirect(f"/main/gradesheet_view/{reg_no}")
            except:
                return render(request, 'main/404.html')
                # return generate_pdf(request, session, reg_no)

    teachers = Teacher.objects.all()
    batches_collection = Batch.objects.all()
    batches = list()
    for batch in batches_collection:
        new_dict = dict()
        semester_list = Semester.objects.filter(batch_no=batch.batch_no)
        new_list = list()
        for semester in semester_list:
            new_list.append(semester)
        new_dict['batch_no'] = batch.batch_no
        new_dict['session'] = batch.session
        new_dict['semesters'] = new_list
        students = Student.objects.filter(batch_no=batch.batch_no)
        batches.append(new_dict)

    return render(request, 'main/dashboard.html', {'batches': batches, 'teachers': teachers})


def semester_view(request, batch_no, semester_no):
    teachers = Teacher.objects.all()
    courses = Course.objects.filter(batch_no=batch_no, semester_no=semester_no)
    students = Student.objects.filter(batch_no=batch_no)
    result_objects = Result.objects.filter(
        batch_no=batch_no, semester_no=semester_no)

    table_sheet = list()
    for result in result_objects:
        a_record = dict()
        a_record['reg_no'] = result.reg_no
        student = Student.objects.filter(
            batch_no=batch_no, reg_no=result.reg_no).first()
        a_record['name'] = student.name
        a_record['batch_no'] = result.batch_no
        a_record['semester_no'] = result.semester_no
        a_record['course_results'] = json.loads(result.course_results)
        a_record['current_semester_credits'] = result.current_semester_credits

        # ********* Current semester GPA: **********************
        a_record['current_semester_GPA'] = result.current_semester_GPA
        # ******************************************************

        # ********* Current semester LG: **********************
        GPA = result.current_semester_GPA
        a_record['current_semester_LG'] = calculate_LG(GPA)
        # ******************************************************

        # ******** Overall credits, CGPA, LG *******************
        if result.semester_no > 1:
            prev_results = []
            for sem in range(1, semester_no):
                try:
                    semester = Result.objects.get(
                        batch_no=batch_no, reg_no=result.reg_no, semester_no=sem)
                    prev_results.append(semester)
                except:
                    pass

            overall_credits, overall_point = result.current_semester_credits, result.current_semester_total_point

            for res in prev_results:
                overall_credits += res.current_semester_credits
                overall_point += res.current_semester_total_point

            a_record['overall_credits'] = overall_credits
            a_record['overall_CGPA'] = round(
                (overall_point/overall_credits), 2)

            CGPA = a_record['overall_CGPA']
            a_record['overall_LG'] = calculate_LG(CGPA)
        # ******************************************************

            a_record['range'] = range(
                2*(len(courses)-len(a_record['course_results'])))

        table_sheet.append(a_record)

    if request.method == "POST":
        batch_no = batch_no
        semester_no = semester_no
        course_code = request.POST['course_code']
        course_title = request.POST['course_title']
        course_credits = request.POST['course_credits']
        course_type = request.POST['course_type']
        course_teacher_email = request.POST['course_teacher_email']
        course_teacher_obj = Teacher.objects.filter(
            email=course_teacher_email).first()
        course_teacher = course_teacher_obj.name

        course = Course.objects.create(batch_no=batch_no,
                                       semester_no=semester_no,
                                       course_code=course_code,
                                       course_title=course_title,
                                       course_credits=course_credits,
                                       course_type=course_type,
                                       course_teacher=course_teacher)

        courses = Course.objects.filter(
            batch_no=batch_no, semester_no=semester_no)

        result = Result.objects.filter(
            batch_no=batch_no, semester_no=semester_no)

        context = {'batch_no': batch_no, 'semester_no': semester_no, 'courses': courses,
                   'result': result, 'table_sheet': table_sheet, 'teachers': teachers}

        return render(request, 'main/semester_view.html', context)

    context = {'batch_no': batch_no, 'semester_no': semester_no,
               'courses': courses, 'table_sheet': table_sheet, 'teachers': teachers}

    return render(request, 'main/semester_view.html', context)


def course_view(request, batch_no, semester_no, course_type, course_code):

    course = Course.objects.get(
        batch_no=batch_no, semester_no=semester_no, course_code=course_code)
    students = Student.objects.filter(batch_no=batch_no)
    course_teacher = Teacher.objects.filter(name=course.course_teacher).first()
    teacher_email = course_teacher.email

    if request.method == "POST":
        if course_type == "Theory":
            reg_no = request.POST['reg_no']
            part_a_decode = request.POST['part_a_decode']
            part_a_marks = request.POST['part_a_marks']
            part_b_decode = request.POST['part_b_decode']
            part_b_marks = request.POST['part_b_marks']
            assessment_marks = request.POST['assessment_marks']
            total_marks = request.POST['total_marks']
            GP = request.POST['GP']
            LG = request.POST['LG']

            TheoryCourseResult.objects.create(reg_no=reg_no,
                                              batch_no=batch_no,
                                              semester_no=semester_no,
                                              course_code=course_code,
                                              part_a_decode=part_a_decode,
                                              part_a_marks=part_a_marks,
                                              part_b_decode=part_b_decode,
                                              part_b_marks=part_b_marks,
                                              assessment_marks=assessment_marks,
                                              total_marks=total_marks,
                                              GP=float(GP),
                                              LG=LG)

            results = TheoryCourseResult.objects.filter(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)

        elif course_type == "Sessional":
            reg_no = request.POST['reg_no']
            lab_marks = request.POST['lab_marks']
            assessment_marks = request.POST['assessment_marks']
            total_marks = request.POST['total_marks']
            GP = request.POST['GP']
            LG = request.POST['LG']

            SessionalCourseResult.objects.create(reg_no=reg_no,
                                                 batch_no=batch_no,
                                                 semester_no=semester_no,
                                                 course_code=course_code,
                                                 lab_marks=lab_marks,
                                                 assessment_marks=assessment_marks,
                                                 total_marks=total_marks,
                                                 GP=float(GP),
                                                 LG=LG)

            results = SessionalCourseResult.objects.filter(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)

        # try to get the Result for this particular reg_no, then update this :
        try:
            result_individual = Result.objects.get(
                reg_no=reg_no, batch_no=batch_no, semester_no=semester_no)
            course_results = json.loads(result_individual.course_results)
            course_results[course.course_code] = {'credits': course.course_credits,
                                                  'GP': GP,
                                                  'LG': LG}
            result_individual.course_results = json.dumps(course_results)
            if float(GP) >= 2:
                result_individual.current_semester_credits += course.course_credits
                result_individual.current_semester_total_point += float(
                    GP)*course.course_credits
                result_individual.current_semester_GPA = round(
                    (result_individual.current_semester_total_point / result_individual.current_semester_credits), 2)

            result_individual.save()

        # if there are no Result found for this particular reg_no, then create one:
        except:
            # *****Finding the result of this course and converting into JSON*****
            course_results = dict()
            course_results[course.course_code] = {'credits': course.course_credits,
                                                  'GP': GP,
                                                  'LG': LG}
            # converting the dict to str(JSON)
            course_results_json = json.dumps(course_results)
            # ********************************************************************

            # **********Finding current semester total credits and total points**********
            if float(GP) >= 2:
                current_semester_credits = course.course_credits
                current_semester_total_point = round(
                    (float(GP) * current_semester_credits), 2)
                current_semester_GPA = float(GP)
            else:
                current_semester_credits = 0
                current_semester_total_point = 0
                current_semester_GPA = 0
            # ***************************************************************************

            result_individual = Result.objects.create(reg_no=reg_no,
                                                      batch_no=batch_no,
                                                      semester_no=semester_no,
                                                      course_results=course_results_json,
                                                      current_semester_credits=current_semester_credits,
                                                      current_semester_total_point=current_semester_total_point,
                                                      current_semester_GPA=current_semester_GPA)

        context = {'course': course, 'results': results,
                   'students': students, 'teacher_email': teacher_email}
        return render(request, 'main/course_view.html', context)

    else:   # if not a POST request
        if course_type == "Theory":
            results = TheoryCourseResult.objects.filter(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        elif course_type == "Sessional":
            results = SessionalCourseResult.objects.filter(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)

        context = {'course': course, 'results': results,
                   'students': students, 'teacher_email': teacher_email}
        return render(request, 'main/course_view.html', context)


def add_semester(request, batch_no):
    semesters = Semester.objects.filter(batch_no=batch_no)
    semester_no = len(semesters)+1
    Semester.objects.create(batch_no=batch_no, semester_no=semester_no)
    return redirect('/main/')


def update_course(request, batch_no, semester_no, course_code):
    if request.method == "POST":
        course_title = request.POST['course_title']
        course_teacher = request.POST['course_teacher']
        course = Course.objects.filter(
            batch_no=batch_no, semester_no=semester_no, course_code=course_code).first()
        course.course_title, course.course_teacher = course_title, course_teacher
        course.save()
        return redirect(f"/main/semesters/{batch_no}/{semester_no}")
    else:
        record = Course.objects.get(
            batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        fm = UpdateCourse(instance=record)
    context = {'form': fm}
    return render(request, 'main/update_course.html', context)


def update_student(request, batch_no, reg_no):
    # the student whose record has to be updated...
    student = Student.objects.filter(reg_no=reg_no).first()

    if request.method == "POST":
        name = request.POST['name']
        father_name = request.POST['father_name']
        mother_name = request.POST['mother_name']
        address = request.POST['address']
        phone = request.POST['phone']
        try:
            request.POST["isCR"]
            isCR = True
        except:
            isCR = False
        try:
            request.POST["isResidential"]
            isResidential = True
        except:
            isResidential = False
        remarks = request.POST['remarks']
        # updating the record...
        student.name = name
        student.father_name = father_name
        student.mother_name = mother_name
        student.address = address
        student.phone = phone
        student.isResidential = isResidential
        student.isCR = isCR
        student.remarks = remarks
        student.save()

        return redirect(f"/main/students/{batch_no}")
    else:
        fm = UpdateStudent(instance=student)
    context = {'form': fm}
    return render(request, 'main/update_student.html', context)


def delete_batch(request, batch_no):
    try:
        batch = Batch.objects.get(batch_no=batch_no)
        batch.delete()
    except:
        pass
    return redirect("/main/")


def delete_teacher(request, name):
    try:
        teacher = Teacher.objects.filter(name=name).first()
        # finding the user who has the same email
        user = User.objects.filter(email=teacher.email).first()
        teacher.delete()
        user.delete()
    except:
        pass
    return redirect("/main/")


def delete_student(request, batch_no, reg_no):
    try:
        student = Student.objects.get(batch_no=batch_no, reg_no=reg_no)
        student.delete()
    except:
        pass
    return redirect(f"/main/students/{batch_no}")


def students_view(request, batch_no):
    students = Student.objects.filter(batch_no=batch_no)
    try:
        batch = Batch.objects.filter(batch_no=batch_no).first()
        session = batch.session
    except:
        batch, session = "", ""

    if request.method == "POST":
        reg_no = request.POST["reg_no"]
        name = request.POST["name"]
        father_name = request.POST["father_name"]
        mother_name = request.POST["mother_name"]
        address = request.POST["address"]
        phone = request.POST["phone"]
        remarks = request.POST["remarks"]
        try:
            request.POST["is_cr"]
            isCR = True
        except:
            isCR = False
        try:
            request.POST["is_residential"]
            isResidential = True
        except:
            isResidential = False

        Student.objects.create(
            reg_no=reg_no,
            batch_no=batch_no,
            session=session,
            name=name,
            father_name=father_name,
            mother_name=mother_name,
            address=address,
            phone=phone,
            isCR=isCR,
            isResidential=isResidential,
            remarks=remarks
        )

        students = Student.objects.filter(batch_no=batch_no)

    return render(request, 'main/students.html', {'batch_no': batch_no, 'session': session, 'students': students})


def teacher_profile(request, institute, department, name):
    teacher = Teacher.objects.filter(
        institute=institute, department=department, name=name).first()
    courses = Course.objects.filter(course_teacher=teacher.name)

    context = {'teacher': teacher, 'courses': courses}
    return render(request, 'main/teacher_profile.html', context)


def calculate_LG(GP):
    if GP == 4.00:
        LG = "A+"
    elif GP >= 3.75:
        LG = "A"
    elif GP >= 3.50:
        LG = "A-"
    elif GP >= 3.25:
        LG = "B+"
    elif GP >= 3.00:
        LG = "B"
    elif GP >= 2.75:
        LG = "B-"
    elif GP >= 2.50:
        LG = "C+"
    elif GP >= 2.25:
        LG = "C"
    elif GP >= 2.00:
        LG = "C-"
    else:
        LG = "F"
    return LG


# ************ EVERYTHING BELOW IS EXPERIMENTAL *************


def assessments(request, batch_no, semester_no, course_code):
    students = Student.objects.filter(batch_no=batch_no)

    if request.method == "POST":
        if request.POST['form_name'] == 'add_tt_form':
            total_marks = int(request.POST['total_marks'])
            try:  # if there is already an instance of AssessmentResult for this course
                assessment = AssessmentResult.objects.get(
                    batch_no=batch_no, semester_no=semester_no, course_code=course_code)
                tt_results = json.loads(assessment.tt_results)
                a_tt = dict()
                a_tt['total_marks'] = total_marks
                a_tt['results'] = list()
                tt_results.append(a_tt)
                tt_results_json = json.dumps(tt_results)
                assessment.tt_results = tt_results_json
                assessment.save()
                assignment_results = json.loads(assessment.assignment_results)
                tt_counting_on = assessment.tt_counting_on
                assignment_counting_on = assessment.assignment_counting_on
            except:  # if there is no instance of AssessmentResult for this course
                tt_results = list()
                a_tt = dict()
                a_tt['total_marks'] = total_marks
                a_tt['results'] = list()
                tt_results.append(a_tt)
                tt_results_json = json.dumps(tt_results)
                tt_counting_on = 20
                assignment_results = list()
                assignment_counting_on = 10
                AssessmentResult.objects.create(
                    batch_no=batch_no,
                    semester_no=semester_no,
                    course_code=course_code,
                    tt_mode="average",
                    tt_counting_on=tt_counting_on,
                    tt_results=tt_results_json,
                    assignment_counting_on=assignment_counting_on,
                    assignment_results="[]",
                    attendance_counting_on=10,
                    attendance_results="[]"
                )
            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'add_assignment_form':
            total_marks = int(request.POST['total_marks'])
            try:  # if there is already an instance of AssessmentResult for this course
                assessment = AssessmentResult.objects.get(
                    batch_no=batch_no, semester_no=semester_no, course_code=course_code)
                assignment_results = json.loads(assessment.assignment_results)
                a_assignment = dict()
                a_assignment['total_marks'] = total_marks
                a_assignment['results'] = list()
                assignment_results.append(a_assignment)
                assignment_results_json = json.dumps(assignment_results)
                assessment.assignment_results = assignment_results_json
                assessment.save()
                tt_results = json.loads(assessment.tt_results)
                tt_mode = assessment.tt_mode
                tt_counting_on = assessment.tt_counting_on
                assignment_counting_on = assessment.assignment_counting_on
            except:  # if there is no instance of AssessmentResult for this course
                assignment_results = list()
                a_assignment = dict()
                a_assignment['total_marks'] = total_marks
                a_assignment['results'] = list()
                assignment_results.append(a_assignment)
                assignment_results_json = json.dumps(assignment_results)
                tt_results = list()
                tt_counting_on = 20
                assignment_counting_on = 10
                tt_mode = "average"
                AssessmentResult.objects.create(
                    batch_no=batch_no,
                    semester_no=semester_no,
                    course_code=course_code,
                    tt_mode=tt_mode,
                    tt_counting_on=tt_counting_on,
                    tt_results="[]",
                    assignment_results=assignment_results_json,
                    assignment_counting_on=assignment_counting_on,
                    attendance_counting_on=10,
                    attendance_results="[]"
                )
            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'add_tt_marks_form':
            tt_no = int(request.POST['tt_no'])
            reg_no = request.POST['reg_no']
            student = Student.objects.get(reg_no=reg_no)
            name = student.name
            obtained_marks = int(request.POST['obtained_marks'])
            assessment = AssessmentResult.objects.get(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)
            tt_results = json.loads(assessment.tt_results)
            a_record = [reg_no, name, obtained_marks]
            tt_results[tt_no-1]['results'].append(a_record)
            tt_results_json = json.dumps(tt_results)
            assessment.tt_results = tt_results_json
            assessment.save()
            assignment_results = json.loads(assessment.assignment_results)
            tt_mode = assessment.tt_mode
            tt_counting_on = assessment.tt_counting_on
            assignment_counting_on = assessment.assignment_counting_on

            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'add_assignment_marks_form':
            assignment_no = int(request.POST['assignment_no'])
            reg_no = request.POST['reg_no']
            student = Student.objects.get(reg_no=reg_no)
            name = student.name
            obtained_marks = int(request.POST['obtained_marks'])
            assessment = AssessmentResult.objects.get(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)
            assignment_results = json.loads(assessment.assignment_results)
            a_record = [reg_no, name, obtained_marks]
            assignment_results[assignment_no-1]['results'].append(a_record)
            assignment_results_json = json.dumps(assignment_results)
            assessment.assignment_results = assignment_results_json
            assessment.save()
            tt_results = json.loads(assessment.tt_results)
            tt_mode = assessment.tt_mode
            tt_counting_on = assessment.tt_counting_on
            assignment_counting_on = assessment.assignment_counting_on

            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'tt_info_submit_form':
            tt_mode = request.POST['tt_mode']
            tt_counting_on = int(request.POST['counting_on'])
            try:
                assessment = AssessmentResult.objects.get(
                    batch_no=batch_no, semester_no=semester_no, course_code=course_code)
                assessment.tt_mode = tt_mode
                assessment.tt_counting_on = tt_counting_on
                assessment.save()
                tt_results = json.loads(assessment.tt_results)
                assignment_results = json.loads(assessment.assignment_results)
                assignment_counting_on = assessment.assignment_counting_on
            except:
                tt_results, assignment_results = [], []
                assignment_counting_on = 10
                AssessmentResult.objects.create(
                    batch_no=batch_no,
                    semester_no=semester_no,
                    course_code=course_code,
                    tt_mode=tt_mode,
                    tt_counting_on=tt_counting_on,
                    tt_results="[]",
                    assignment_counting_on=assignment_counting_on,
                    assignment_results="[]",
                    attendance_counting_on=10,
                    attendance_results="[]"
                )
            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'assignment_info_submit_form':
            assignment_counting_on = int(request.POST['counting_on'])
            try:
                assessment = AssessmentResult.objects.get(
                    batch_no=batch_no, semester_no=semester_no, course_code=course_code)
                assessment.assignment_counting_on = assignment_counting_on
                assessment.save()
                tt_results = json.loads(assessment.tt_results)
                assignment_results = json.loads(assessment.assignment_results)
                tt_counting_on = assessment.tt_counting_on
                tt_mode = assessment.tt_mode
            except:
                AssessmentResult.objects.create(
                    batch_no=batch_no,
                    semester_no=semester_no,
                    course_code=course_code,
                    tt_mode="average",
                    tt_counting_on=20,
                    tt_results="[]",
                    assignment_counting_on=10,
                    assignment_results="[]",
                    attendance_counting_on=10,
                    attendance_results="[]"
                )
            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

        elif request.POST['form_name'] == 'attendance_info_submit_form':
            attendance_counting_on = int(request.POST['counting_on'])
            try:
                assessment = AssessmentResult.objects.get(
                    batch_no=batch_no, semester_no=semester_no, course_code=course_code)
                assessment.attendance_counting_on = attendance_counting_on
                assessment.save()
            except:
                AssessmentResult.objects.create(
                    batch_no=batch_no,
                    semester_no=semester_no,
                    course_code=course_code,
                    tt_mode="average",
                    tt_counting_on=20,
                    tt_results="[]",
                    assignment_counting_on=10,
                    assignment_results="[]",
                    attendance_counting_on=attendance_counting_on,
                    attendance_results="[]"
                )
            return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

    # if it is a GET request:
    try:
        assessment = AssessmentResult.objects.get(
            batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        # for term tests:
        tt_results = json.loads(assessment.tt_results)
        tt_mode = assessment.tt_mode
        tt_counting_on = assessment.tt_counting_on
        # for assignments:
        assignment_results = json.loads(assessment.assignment_results)
        assignment_counting_on = assessment.assignment_counting_on
        # for attendance:
        attendance_results = json.loads(assessment.attendance_results)
        attendance_counting_on = assessment.attendance_counting_on
    except:
        tt_results = []
        assignment_results = []
        attendance_results = []
        tt_mode = "average"
        tt_counting_on = 20
        assignment_counting_on = 10
        attendance_counting_on = 10

    context = {
        'batch_no': batch_no,
        'semester_no': semester_no,
        'course_code': course_code,
        'students': students,
        'tt_results': tt_results,
        'tt_mode': tt_mode,
        'tt_counting_on': tt_counting_on,
        'assignment_results': assignment_results,
        'assignment_counting_on': assignment_counting_on,
        'attendance_results': attendance_results,
        'attendance_counting_on': attendance_counting_on
    }

    return render(request, 'main/assessment.html', context)


def add_attendance(request, batch_no, semester_no, course_code):
    students = Student.objects.filter(batch_no=batch_no)

    if request.method == "POST":
        equal_to = int(request.POST['equal_to'])
        try:
            assessment = AssessmentResult.objects.get(
                batch_no=batch_no, semester_no=semester_no, course_code=course_code)
            attendance_results = json.loads(assessment.attendance_results)
            a_class = dict()
            a_class['equal_to'] = equal_to
            attendance = list()
            for student in students:
                try:
                    att = request.POST[student.reg_no]
                    att_class = equal_to
                except:
                    att_class = 0
                attendance.append([student.reg_no, student.name, att_class])
                a_class['attendance'] = attendance
            attendance_results.append(a_class)
            attendance_results_json = json.dumps(attendance_results)
            assessment.attendance_results = attendance_results_json
            assessment.save()
        except:
            attendance_results = list()
            a_class = dict()
            a_class['equal_to'] = equal_to
            a_class['attendance'] = list()
            for student in students:
                try:
                    att = request.POST[student.reg_no]
                    att_class = equal_to
                except:
                    att_class = 0
                a_class['attendance'].append(
                    [student.reg_no, student.name, att_class])
            attendance_results.append(a_class)
            attendance_results_json = json.dumps(attendance_results)

            AssessmentResult.objects.create(
                batch_no=batch_no,
                semester_no=semester_no,
                course_code=course_code,
                tt_mode="average",
                tt_counting_on=20,
                tt_results="[]",
                assignment_counting_on=10,
                assignment_results="[]",
                attendance_counting_on=10,
                attendance_results=attendance_results_json
            )

        return redirect(f"/main/assessments/{batch_no}/{semester_no}/{course_code}")

    context = {
        'students': students,
        'batch_no': batch_no,
        'semester_no': semester_no,
        'course_code': course_code
    }
    return render(request, 'main/add_attendance.html', context)


def overall_assessment(request, batch_no, semester_no, course_code):
    assessment = AssessmentResult.objects.get(
        batch_no=batch_no, semester_no=semester_no, course_code=course_code)
    tt_results = json.loads(assessment.tt_results)
    assignment_results = json.loads(assessment.assignment_results)
    attendance_results = json.loads(assessment.attendance_results)
    tt_mode = assessment.tt_mode
    tt_counting_on = assessment.tt_counting_on
    assignment_counting_on = assessment.assignment_counting_on
    attendance_counting_on = assessment.attendance_counting_on
    students = Student.objects.filter(batch_no=batch_no)

    full_batch_overall_assessment_marks = list()

    for i, student in enumerate(students):
        a_std = list()
        a_std.append(student.reg_no)
        a_std.append(student.name)
        all_tt_marks = list()
        all_assignment_marks = list()
        all_attendance_marks = list()

        # calculating tt marks
        for tt_res in tt_results:
            obtained_marks = tt_res['results'][i][2]
            total_marks = tt_res['total_marks']
            all_tt_marks.append([obtained_marks, total_marks])
        a_std_final_tt_marks = calculate_overall_marks(
            tt_mode, tt_counting_on, all_tt_marks)
        a_std.append(a_std_final_tt_marks)

        # calculating assignment marks
        for ass_res in assignment_results:
            obtained_marks = ass_res['results'][i][2]
            total_marks = ass_res['total_marks']
            all_assignment_marks.append([obtained_marks, total_marks])
        a_std_final_assignment_marks = calculate_overall_marks(
            "average", assignment_counting_on, all_assignment_marks)
        a_std.append(a_std_final_assignment_marks)

        # calculating attendance marks
        for att_res in attendance_results:
            attended_classes = att_res['attendance'][i][2]
            equal_to = att_res['equal_to']
            all_attendance_marks.append([attended_classes, equal_to])
        a_std_final_attendance_marks = calculate_attendance(
            attendance_counting_on, all_attendance_marks)
        a_std.append(a_std_final_attendance_marks)

        a_std_final_marks = a_std_final_tt_marks + \
            a_std_final_assignment_marks + a_std_final_attendance_marks
        a_std.append(a_std_final_marks)

        # finally getting all records of tt and assignments
        full_batch_overall_assessment_marks.append(a_std)

    context = {
        'batch_no': batch_no,
        'semester_no': semester_no,
        'course_code': course_code,
        'full_batch_overall_assessment_marks': full_batch_overall_assessment_marks
    }

    return render(request, 'main/overall_assessment.html', context)
    # return HttpResponse(full_batch_overall_assessment_marks)


# e.g. ("normal", 20, [[8,10], [9,10]])
def calculate_overall_marks(mode, counting_on, results):
    final_marks = 0
    if mode == "normal":
        for result in results:
            final_marks += result[0]

    elif mode == "average":
        num = len(results)
        total_marks = 0
        for result in results:
            total_marks += int((counting_on/result[1])*result[0])
        try:
            final_marks = ceil(total_marks/num)
        except:
            final_marks = 0

    elif mode == "best_one":
        marks = []
        for result in results:
            marks.append(int((counting_on/result[1])*result[0]))
        final_marks = max(marks)

    elif mode == "best_two":
        marks = []
        for result in results:
            marks.append(int((counting_on/result[1])*result[0]))
        best = marks.pop(marks.index(max(marks))) // int(counting_on/result[1])
        second_best = marks.pop(marks.index(max(marks))
                                ) // int(counting_on/result[1])
        final_marks = (best + second_best) // 2

    return final_marks


# e.g. (10, [ [1,1],[0,2],[2,2],[1,1] ])
def calculate_attendance(counting_on, results):
    total_classes = 0
    attended_classes = 0
    for result in results:
        total_classes += result[1]
        attended_classes += result[0]
    try:
        final_marks = ceil((attended_classes/total_classes)*counting_on)
    except:
        final_marks = 0

    return final_marks


def semester_name(semester_no):
    if semester_no == 1:
        return "First Year First Semester"
    elif semester_no == 2:
        return "First Year Second Semester"
    elif semester_no == 3:
        return "Second Year First Semester"
    elif semester_no == 4:
        return "Second Year Second Semester"
    elif semester_no == 5:
        return "Third Year First Semester"
    elif semester_no == 6:
        return "Third Year Second Semester"
    elif semester_no == 7:
        return "Fourth Year First Semester"
    elif semester_no == 8:
        return "Fourth Year Second Semester"


def gradesheet_view(request, reg_no):
    student = Student.objects.get(reg_no=reg_no)
    session = student.session
    batch = Batch.objects.get(session=session)
    batch_no = batch.batch_no
    student = Student.objects.get(reg_no=reg_no)
    student_name = student.name

    gradesheet = list()
    semester_results = Result.objects.filter(reg_no=reg_no)
    cumulative_credits, cumulative_point, cumulative_LG = float(
        0), float(0), 'NA'   # for the overall result of all semesters
    inc = 1
    for result in semester_results:
        a_semester = dict()
        course_results = json.loads(result.course_results)
        course_results_info = list()
        this_semester_credits, this_semester_point, this_semester_LG = float(
            0), float(0), 'NA'   # for only a particular semester
        for cour in course_results.items():
            course_info = list()
            # pushing the course_code at index=0
            course_info.append(cour[0])
            course = Course.objects.filter(
                batch_no=batch_no, course_code=cour[0]).first()
            # pushing the course_title at index=1
            course_info.append(course.course_title)
            # pushing the course_credits at index=2
            course_info.append(course.course_credits)
            # pushing the obtained GP at index=3
            course_info.append(cour[1]['GP'])
            # pushing the obtained LG at index=4
            course_info.append(cour[1]['LG'])
            # checking if the obtained GP >= 2
            if float(course_info[3]) >= 2:
                # cumulative_credits += course_credits
                this_semester_credits += course_info[2]
                # cumulative_point += GP * course_credits
                this_semester_point += float(course_info[3]) * course_info[2]
            course_results_info.append(course_info)

        a_semester['this_semester_name'] = semester_name(inc)
        inc += 1
        a_semester['this_semester_credits'] = this_semester_credits
        a_semester['course_results_info'] = course_results_info

        this_semester_GP = round(
            (this_semester_point/this_semester_credits), 2)
        a_semester['this_semester_GP'] = this_semester_GP

        if this_semester_GP == 4.00:
            this_semester_LG = "A+"
        elif this_semester_GP >= 3.75:
            this_semester_LG = "A"
        elif this_semester_GP >= 3.50:
            this_semester_LG = "A-"
        elif this_semester_GP >= 3.25:
            this_semester_LG = "B+"
        elif this_semester_GP >= 3.00:
            this_semester_LG = "B"
        elif this_semester_GP >= 2.75:
            this_semester_LG = "B-"
        elif this_semester_GP >= 2.50:
            this_semester_LG = "C+"
        elif this_semester_GP >= 2.25:
            this_semester_LG = "C"
        elif this_semester_GP >= 2.00:
            this_semester_LG = "C-"
        else:
            this_semester_LG = "F"
        a_semester['this_semester_LG'] = this_semester_LG

        cumulative_credits += this_semester_credits
        a_semester['cumulative_credits'] = cumulative_credits
        cumulative_point += this_semester_point
        cumulative_GP = round((cumulative_point/cumulative_credits), 2)
        a_semester['cumulative_GP'] = cumulative_GP

        if cumulative_GP == 4.00:
            cumulative_LG = "A+"
        elif cumulative_GP >= 3.75:
            cumulative_LG = "A"
        elif cumulative_GP >= 3.50:
            cumulative_LG = "A-"
        elif cumulative_GP >= 3.25:
            cumulative_LG = "B+"
        elif cumulative_GP >= 3.00:
            cumulative_LG = "B"
        elif cumulative_GP >= 2.75:
            cumulative_LG = "B-"
        elif cumulative_GP >= 2.50:
            cumulative_LG = "C+"
        elif cumulative_GP >= 2.25:
            cumulative_LG = "C"
        elif cumulative_GP >= 2.00:
            cumulative_LG = "C-"
        else:
            cumulative_LG = "F"
        a_semester['cumulative_LG'] = cumulative_LG

        gradesheet.append(a_semester)

    # print(gradesheet)

    li = []
    a = []
    for i in range(len(gradesheet)):
        if i % 2 == 0:
            a = gradesheet[i]
        else:
            try:
                b = []
                b.append(a)
                b.append(gradesheet[i])
                li.append(b)
            except:
                li.append(a)
    if len(gradesheet) % 2 == 1:
        b = []
        b.append(a)
        li.append(b)

    for couple in li:
        for single in couple:
            print(single)

    return render(request, 'main/gradesheet_view.html', {'session': session, 'reg_no': reg_no, 'student_name': student_name, 'gradesheet': gradesheet, 'collection': li})


