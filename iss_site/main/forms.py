from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.forms import ModelForm, TextInput, Textarea, Select, EmailField, RegexField, IntegerField
from django.contrib.auth.models import User
from django import forms
from .models import *


class AuthForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black text-base outline-none text-black py-1 px-3 leading-4 transition-colors duration-200 ease-in-out',
               'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black text-base outline-none text-gray-700 py-1 px-3 leading-4 transition-colors duration-200 ease-in-out',
            'placeholder': 'Пароль'}))

class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'telegram']

    first_name = UsernameField(widget=forms.TextInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black text-base outline-none text-[#191D32] py-1 px-3 leading-4',
            'placeholder': 'Имя',
            'disabled':'true'}))
    last_name = UsernameField(widget=forms.TextInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black text-base outline-none text-[#191D32] py-1 px-4 leading-4',
            'placeholder': 'Фамилия',
            'disabled':'true'}))
    email = EmailField(widget=forms.TextInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black invalid:border-red-500 invalid:text-red-600 focus:invalid:border-red-500 focus:invalid:ring-red-500 text-base outline-none text-[#191D32] py-1 px-3 leading-4',
            'placeholder': 'Электронная почта'}))
    phone = RegexField(regex=r'^\+?1?\d{9,15}$', widget=forms.TextInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black invalid:border-red-500 invalid:text-red-600 focus:invalid:border-red-500 focus:invalid:ring-red-500 text-base outline-none text-[#191D32] py-1 px-3 leading-4',
            'placeholder': 'Электронная почта'}))
    telegram = IntegerField(widget=forms.TextInput(
        attrs={
            'class': 'w-full bg-[#E5FCFF] rounded-[14px] border-2 border-black text-base outline-none text-[#191D32] py-1 px-3 leading-4',
            'placeholder': 'Телеграм'}))