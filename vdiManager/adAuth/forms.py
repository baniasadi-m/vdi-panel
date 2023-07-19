from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput

class CaptchaLoginForm(forms.Form):
   username = forms.CharField(max_length=65)
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)
   captcha=CaptchaField(widget=CaptchaTextInput(attrs={'class': 'form-control'}),label='Please enter the characters in the image')
   

