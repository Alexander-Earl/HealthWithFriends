from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm
from healthwithfriends.models import User, UserPreferences
from django.forms.widgets import DateInput
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        """
        We override the form's 'clean' method, so that if the form passes validation, we check the credentials of the
        user. If it fails, we can raise a form error message.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, invalid login credentials. Please try again.")
        return self.cleaned_data


class SignUpForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'sex', 'email', 'city', 'dob', 'height', 'weight']
        labels = {
            'dob': 'Date of Birth:',
        }
        widgets = {
            'dob': DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
        }


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password'}), label="Old password:")
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password'}), label="New password:")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password'}), label="Confirm new password")

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

