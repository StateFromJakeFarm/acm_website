from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from markdownx.fields import MarkdownxFormField

class ProblemSubmissionForm(forms.Form):
    solution_file = forms.FileField()

class CreateOrEditProblemForm(forms.Form):
    '''
    Manage problem creations and edits
    '''
    title       = forms.CharField()
    description = forms.CharField()
    testcases   = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class RegistrationForm(UserCreationForm):
    '''
    Manage creation of new users
    '''
    email = forms.EmailField(
        label='Email',
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user
