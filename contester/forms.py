from django import forms
from django.contrib.auth.forms import UserCreationForm
from contester.models import Account


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = Account
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class DocumentForm(forms.Form):
	file = forms.FileField(label='Select a file', help_text='max. 1 megabytes')