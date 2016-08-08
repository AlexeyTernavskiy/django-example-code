from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.core import validators


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True,
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True,
        })
        self.fields['remember'].widget = forms.CheckboxInput(attrs={
            'class': 'checkbox',
        })


class CustomSignupForm(SignupForm):
    username = forms.CharField(label='Username',
                               validators=[
                                   validators.MinLengthValidator(limit_value=4,
                                                                 message='Nickname length should be more \
                                                                                 than 3 characters'),
                               ],
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Username',
                                   'required': True,
                               }))
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Password',
                                    'required': True,
                                }))
    password2 = forms.CharField(label='Password (again)',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Password (again)',
                                    'required': True,
                                }))
