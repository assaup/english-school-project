from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'level', 'cover']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }