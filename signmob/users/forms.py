from django import forms
from django.contrib.auth import get_user_model, forms as auth_forms

from allauth.account.forms import SignupForm

User = get_user_model()


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name',)


class CustomSignupForm(SignupForm):
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Dein Name',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(('name', 'email', 'password1', 'password2'))

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user
