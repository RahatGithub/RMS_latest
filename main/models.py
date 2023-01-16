from django.db import models


class Batch(models.Model):
    id = models.AutoField
    batch_no = models.CharField(max_length=6, default="")               
    session = models.CharField(max_length=8, default="")                
    

class Semester(models.Model):
    id = models.AutoField 
    batch_no = models.CharField(max_length=8, default="")
    semester_no = models.IntegerField(default=None)

   
class Course(models.Model):
    id = models.AutoField
    batch_no = models.CharField(max_length=8, default="")
    semester_no = models.IntegerField(default=None)
    course_code = models.CharField(max_length=8, default="")
    course_title = models.CharField(max_length=60, default="")
    course_type =  models.CharField(max_length=10, default="")
    course_credits = models.FloatField(default=0) 
    course_teacher = models.CharField(max_length=40, default="") 


class Student(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    batch_no = models.CharField(max_length=6, default="")
    session = models.CharField(max_length=8, default="")   
    name = models.CharField(max_length=60, default="")
    father_name = models.CharField(max_length=60, default="")
    mother_name = models.CharField(max_length=60, default="")
    address = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=11, default="")
    isResidential = models.BooleanField(default=False)
    isCR = models.BooleanField(default=False) 
    average_cgpa = models.FloatField(default=0)
    remarks = models.CharField(max_length=500, default="")


class Teacher(models.Model):
    id = models.AutoField 
    name = models.CharField(max_length=60, default="")
    designation = models.CharField(max_length=60, default="")
    institute = models.CharField(max_length=100, default="")
    department = models.CharField(max_length=100, default="")


class TheoryCourseResult(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    batch_no = models.CharField(max_length=6, default="")
    semester_no = models.IntegerField(default=None)
    course_code = models.CharField(max_length=8, default="")
    part_a_decode = models.CharField(max_length=10, default="")
    part_a_marks = models.IntegerField(default=None)
    part_b_decode = models.CharField(max_length=10, default="")
    part_b_marks = models.IntegerField(default=None)
    assessment_marks = models.IntegerField(default=None)
    total_marks = models.IntegerField(default=None)
    GP = models.FloatField(default=0)
    LG = models.CharField(max_length=5, default="")


class SessionalCourseResult(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    batch_no = models.CharField(max_length=6, default="")
    semester_no = models.IntegerField(default=None)
    course_code = models.CharField(max_length=8, default="")
    lab_marks = models.IntegerField(default=None)
    assessment_marks = models.IntegerField(default=None)
    total_marks = models.IntegerField(default=None)
    GP = models.FloatField(default=0)
    LG = models.CharField(max_length=5, default="")


class Result(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    batch_no = models.CharField(max_length=6, default="") # take session instead
    semester_no = models.IntegerField(default=None)
    course_results = models.CharField(max_length=1000, default="")
    current_semester_credits = models.FloatField(default=0)
    current_semester_total_point = models.FloatField(default=0)
    current_semester_GPA = models.FloatField(default=0)