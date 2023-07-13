from django import forms
from captcha.fields import CaptchaField

class CaptchaForm(forms.Form):
   captcha=CaptchaField(label='Please enter the characters in the image')

