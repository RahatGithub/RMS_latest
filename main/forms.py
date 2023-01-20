from django import forms 
from .models import Teacher, Course 

# class UpdateCourse(forms.ModelForm):
#     class Meta:
#         model = Course   
#         fields = ['course_title', 'course_teacher'] 
#         widgets = {
#             'course_title' : forms.TextInput(attrs={'class':'form-control'}),
#             'course_teacher' : forms.TextInput(attrs={'class':'form-control'})
#         }

class UpdateCourse(forms.Form):
    teachers = Teacher.objects.all()
    
    teachers_list = list()
    for teacher in teachers:
        a_teacher = (teacher.name, teacher.name)
        teachers_list.append(a_teacher)
    

    course_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    course_teacher = forms.CharField(label='Course Teacher', widget=forms.Select(attrs={'class':'form-control'}, choices=teachers_list))
    