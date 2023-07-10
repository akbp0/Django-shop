from django import forms
from .models import MyUsers, OtpModel
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password", widget=forms.PasswordInput)

    class Meta:
        model = MyUsers
        fields = ("full_name", "phone_number", "email")

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password2"] and cd["password1"] and cd["password1"] != cd["password2"]:
            raise ValidationError("Passwords does not match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='<a href"../password/">change</a>')

    class Meta:
        model = MyUsers
        fields = ("full_name", "phone_number", "email", "password", "last_login")


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email", widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    phone_number = forms.CharField(
        label="Your phone nubmer", widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    full_name = forms.CharField(
        label="Full Name", widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    password1 = forms.CharField(
        label="password", widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    password2 = forms.CharField(
        label='confrim your password', widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = MyUsers.objects.filter(phone_number=phone_number).exists()
        if user:
            raise ValidationError("This phone_number is already in use")
        OtpModel.objects.filter(phone_number=phone_number).delete()
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        user = MyUsers.objects.filter(email=email).exists()
        if user:
            raise ValidationError("This email is already in use")
        return email

    def clean_password(self):
        password1 = self.cleaned_data["password1"]
        if len(password1) < 8:
            raise ValidationError("your password is too short")
        return password1

    def clean(self):
        cd = super().clean()
        pas = cd.get("password1")
        pas2 = cd.get("password2")
        if pas and pas2 and pas2 != pas:
            raise ValidationError("passwords are not same")


class VerifyForm(forms.Form):
    code = forms.IntegerField(
        min_value=10000, max_value=99999, widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )


class LoginForm(forms.Form):
    phone_number = forms.CharField(
        label="password", widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ))
    password = forms.CharField(
        label="password", widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ))
