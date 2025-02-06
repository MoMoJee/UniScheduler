from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# 注册用的表单
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# 对于登录表单，Django 自带的 AuthenticationForm 已经足够使用，无需额外定义。