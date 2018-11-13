from django import forms

class ProblemSubmissionForm(forms.Form):
    solution_file = forms.FileField()
