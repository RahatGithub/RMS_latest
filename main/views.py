from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from .models import Batch, Semester, Course, Student, TheoryCourseResult, SessionalCourseResult, Result, Teacher
from .forms import UpdateCourse
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
            return render(request, 'main/dashboard.html', {'batches' : batches, 'teachers' : teachers}) 
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
            username = (name.replace(" ", "")).lower()[:5] + '_' + str(randint(100,999)) 
            
            # Generating a code/password for the teacher: 
            password =  chr(randint(97,122)) + chr(randint(97,122)) + chr(randint(97,122))+ chr(randint(48,57)) + chr(randint(48,57)) + chr(randint(48,57)) + chr(randint(35,38))
            
            Teacher.objects.create(name=name, email=email, phone=phone, designation=designation, department=department, institute=institute)
            user = User.objects.create_user(username, email, password)
            user.first_name, user.last_name = first_name, last_name
            user.save()
            teachers = Teacher.objects.all()
            batches = Batch.objects.all() 
                
            new_teacher_info = {
                'username' : username,
                'password' : password,
                'email' : email
            }
            return render(request, 'main/dashboard.html', {'batches' : batches, 'teachers' : teachers, 'new_teacher_info' : new_teacher_info})
        elif request.POST['form_name'] == 'gradesheet_generator_form':
            reg_no = request.POST['reg_no']
            student = Student.objects.get(reg_no=reg_no)
            session = student.session 
            # return generate_pdf(request, session, reg_no)
            return HttpResponse("ok")
        
        
    # teachers_collection = Teacher.objects.all()
    # teachers = list()
    # for teacher in teachers_collection:
    #     a_teacher = dict()
    #     a_teacher['name'] = teacher.name
    #     a_teacher['designation'] = teacher.designation
    #     a_teacher['department'] = teacher.department
    #     a_teacher['institute'] = teacher.institute
        
    #     courses_collection = Course.objects.filter(course_teacher=teacher.name)
    #     courses = list()
    #     for course in courses_collection:
    #         courses.append(course)
    #     a_teacher['courses'] = courses 
    #     teachers.append(a_teacher)
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

    return render(request, 'main/dashboard.html', {'batches' : batches, 'teachers' : teachers})



def semester_view(request, batch_no, semester_no):  
    teachers = Teacher.objects.all()
    courses = Course.objects.filter(batch_no=batch_no, semester_no=semester_no)
    students = Student.objects.filter(batch_no=batch_no)
    result_objects = Result.objects.filter(batch_no=batch_no, semester_no=semester_no)
    
    table_sheet = list()
    for result in result_objects:
        a_record = dict()
        a_record['reg_no'] = result.reg_no
        student = Student.objects.filter(batch_no=batch_no, reg_no=result.reg_no).first()
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
                    semester = Result.objects.get(batch_no=batch_no, reg_no=result.reg_no, semester_no=sem)
                    prev_results.append(semester)
                except:
                    pass
            
            overall_credits, overall_point = result.current_semester_credits, result.current_semester_total_point
            
            for res in prev_results:
                overall_credits += res.current_semester_credits
                overall_point += res.current_semester_total_point
            
            a_record['overall_credits'] = overall_credits
            a_record['overall_CGPA'] = round((overall_point/overall_credits), 2) 
            
            CGPA = a_record['overall_CGPA']
            a_record['overall_LG'] = calculate_LG(CGPA)
        # ******************************************************
        
            a_record['range'] = range(2*(len(courses)-len(a_record['course_results'])))
            
        table_sheet.append(a_record)

    if request.method == "POST":
        batch_no = batch_no
        semester_no = semester_no
        course_code = request.POST['course_code']
        course_title = request.POST['course_title']
        course_credits = request.POST['course_credits']
        course_type = request.POST['course_type']
        course_teacher_email = request.POST['course_teacher_email']
        course_teacher_obj = Teacher.objects.filter(email=course_teacher_email).first()
        course_teacher = course_teacher_obj.name 
        
        course = Course.objects.create(batch_no=batch_no, 
                                       semester_no=semester_no, 
                                       course_code=course_code, 
                                       course_title=course_title, 
                                       course_credits=course_credits,
                                       course_type=course_type,
                                       course_teacher=course_teacher)
        
        courses = Course.objects.filter(batch_no=batch_no, semester_no=semester_no)
        
        result = Result.objects.filter(batch_no=batch_no, semester_no=semester_no)
        
        context = {'batch_no':batch_no, 'semester_no':semester_no, 'courses':courses, 'result':result, 'table_sheet':table_sheet, 'teachers':teachers}

        return render(request, 'main/semester_view.html', context)
    
    
    
    context = {'batch_no':batch_no, 'semester_no':semester_no, 'courses':courses, 'table_sheet':table_sheet, 'teachers':teachers}

    return render(request, 'main/semester_view.html', context)



def course_view(request, batch_no, semester_no, course_type, course_code):
    
    course = Course.objects.get(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
    students = Student.objects.filter(batch_no=batch_no)
    course_teacher = Teacher.objects.filter(name=course.course_teacher).first()
    teacher_email = course_teacher.email
    print(teacher_email)

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
                                              LG=LG )
            
            results = TheoryCourseResult.objects.filter(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
            
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
                                                 LG=LG )
            
            results = SessionalCourseResult.objects.filter(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        
        # try to get the Result for this particular reg_no, then update this :
        try: 
            result_individual = Result.objects.get(reg_no=reg_no, batch_no=batch_no, semester_no=semester_no)  
            course_results = json.loads(result_individual.course_results)
            course_results[course.course_code] = {'credits' : course.course_credits,
                                                  'GP' : GP,
                                                  'LG' : LG }
            result_individual.course_results = json.dumps(course_results)
            if float(GP) >= 2: 
                result_individual.current_semester_credits += course.course_credits
                result_individual.current_semester_total_point += float(GP)*course.course_credits  
                result_individual.current_semester_GPA = round((result_individual.current_semester_total_point / result_individual.current_semester_credits), 2)

            result_individual.save()
            
        # if there are no Result found for this particular reg_no, then create one: 
        except:
            # *****Finding the result of this course and converting into JSON*****
            course_results = dict()
            course_results[course.course_code] = {'credits' : course.course_credits,
                                                  'GP' : GP,
                                                  'LG' : LG }
            course_results_json = json.dumps(course_results)  # converting the dict to str(JSON)
            # ********************************************************************
            
            
            # **********Finding current semester total credits and total points**********
            if float(GP) >= 2: 
                current_semester_credits = course.course_credits
                current_semester_total_point = round((float(GP) * current_semester_credits), 2)
                current_semester_GPA = float(GP)
            else : 
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
        
        context = {'course':course,'results':results, 'students':students, 'teacher_email':teacher_email}
        return render(request, 'main/course_view.html', context)
    
    else:   # if not a POST request
        if course_type == "Theory": 
            results = TheoryCourseResult.objects.filter(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        elif course_type == "Sessional":
            results = SessionalCourseResult.objects.filter(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
        
        context = {'course':course,'results':results, 'students':students, 'teacher_email':teacher_email}
        return render(request, 'main/course_view.html', context)




def add_semester(request, batch_no):
    semesters = Semester.objects.filter(batch_no=batch_no)
    semester_no = len(semesters)+1
    Semester.objects.create(batch_no=batch_no, semester_no=semester_no)
    return redirect('/main/')


# def update_course(request, batch_no, semester_no, course_code):
#     if request.method == "POST":
#         record = Course.objects.get(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
#         fm = UpdateCourse(request.POST, instance=record) # Generating a form with the values of the record with the given info
#         if fm.is_valid():
#             fm.save()
#     else:
#         record = Course.objects.get(batch_no=batch_no, semester_no=semester_no, course_code=course_code)
#         fm = UpdateCourse(instance=record) 
    
#     context = {'form' : fm}
#     return render(request, 'main/update_course.html', context)


def update_course(request, batch_no, semester_no, course_code):
    if request.method == "POST":
        course_title = request.POST['course_title']
        course_teacher = request.POST['course_teacher']
        course = Course.objects.filter(batch_no=batch_no, semester_no=semester_no, course_code=course_code).first()
        course.course_title, course.course_teacher = course_title, course_teacher  
        course.save()
        return redirect(f"/main/semesters/{batch_no}/{semester_no}")

    else:
        fm = UpdateCourse()
    
    context = {'form':fm}
    return render(request, 'main/update_course.html', context)



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
        user = User.objects.filter(email=teacher.email).first()  # finding the user who has the same email
        teacher.delete()
        user.delete()
    except:
        pass

    return redirect("/main/")



def students_view(request, batch_no):  
    students = Student.objects.filter(batch_no=batch_no)
    batch = Batch.objects.filter(batch_no=batch_no).first()
    session = batch.session 

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

    return render(request, 'main/students.html', {'batch_no':batch_no, 'session':session, 'students':students})


def teacher_profile(request, institute, department, name):
    teacher = Teacher.objects.filter(institute=institute, department=department, name=name).first() 
    courses = Course.objects.filter(course_teacher=teacher.name)

    context = {'teacher':teacher, 'courses':courses}
    return render(request, 'main/teacher_profile.html', context)



def calculate_LG(GP):
    if GP == 4.00 : LG = "A+"
    elif GP >= 3.75 : LG = "A"
    elif GP >= 3.50 : LG = "A-" 
    elif GP >= 3.25 : LG = "B+"
    elif GP >= 3.00 : LG = "B"
    elif GP >= 2.75 : LG = "B-"
    elif GP >= 2.50 : LG = "C+"
    elif GP >= 2.25 : LG = "C"
    elif GP >= 2.00 : LG = "C-" 
    else: LG = "F"
    return LG 