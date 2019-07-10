from django import forms

from signmob.users.forms import CustomSignupForm

from .models import CollectionGroup, CollectionGroupMember


class GroupSignupForm(CustomSignupForm):
    group = forms.ModelChoiceField(
        queryset=CollectionGroup.objects.all(),
        widget=forms.HiddenInput
    )

    def save(self, request):
        user = super().save(request)

        CollectionGroupMember.objects.create(
            group=self.cleaned_data['group'],
            user=user
        )

        return user
