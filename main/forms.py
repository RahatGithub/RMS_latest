from django import forms 
from .models import Teacher, Course, Student


class UpdateCourse(forms.ModelForm):
    class Meta:
        model = Course   
        fields = ['course_title', 'course_teacher'] 
        
        teachers = Teacher.objects.all()
        teachers_list = list()
        for teacher in teachers:
            a_teacher = (teacher.name, teacher.name)
            teachers_list.append(a_teacher)

        widgets = {
            'course_title' : forms.TextInput(attrs={'class':'form-control'}),
            'course_teacher' : forms.Select(attrs={'class':'form-control'}, choices=teachers_list)
        }


class UpdateStudent(forms.ModelForm):
    class Meta:
        model = Student   
        fields = ['name', 'father_name', 'mother_name', 'address', 'phone', 'isResidential', 'isCR', 'remarks'] 

        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'father_name' : forms.TextInput(attrs={'class':'form-control'}),
            'mother_name' : forms.TextInput(attrs={'class':'form-control'}),
            'address' : forms.TextInput(attrs={'class':'form-control'}),
            'phone' : forms.TextInput(attrs={'class':'form-control'}),
            'isResidential' : forms.CheckboxInput(),
            'isCR' : forms.CheckboxInput(),
            'remarks' : forms.Textarea(attrs={'class':'form-control'})
        }