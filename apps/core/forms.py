from django import forms
from .models import ContactInquiry


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'company', 'phone', 'email', 'message']
        labels = {
            'name': 'Ваше имя',
            'company': 'Компания',
            'phone': 'Телефон',
            'email': 'Email',
            'message': 'Описание задачи',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Иван Иванов', 'class': 'form__input'}),
            'company': forms.TextInput(attrs={'placeholder': 'ТОО «Компания»', 'class': 'form__input'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__', 'class': 'form__input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@company.kz', 'class': 'form__input'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите вашу задачу...', 'class': 'form__textarea'}),
        }
