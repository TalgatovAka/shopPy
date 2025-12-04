from django import forms
from django.contrib.auth.models import User
from .models import Product
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, help_text="Пароль: цифры и буквы.", required=True)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("Логин может содержать только латинские буквы, цифры и _")
        return username

    def clean_password(self):
        p = self.cleaned_data.get("password")
        validate_password(p)
        if not re.match(r'^[A-Za-z0-9]+$', p):
            raise ValidationError("Пароль может содержать только латинские буквы и цифры")
        return p

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password2"):
            raise ValidationError("Пароли не совпадают")
        return cleaned

class LoginForm(forms.Form):
    identifier = forms.CharField(label="Логин или Email")
    password = forms.CharField(widget=forms.PasswordInput)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "manufacturer", "release_date", "weight", "price", "photo", "description"]
        widgets = {
            "release_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

