from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

# forms d'enregistrement
class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'last_name', 'first_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')