from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

from leaflet.forms.widgets import LeafletWidget

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


user_detail_view = UserDetailView.as_view()


class KiezWidget(LeafletWidget):
    geom_type = 'Point'


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name", "mobile", "geo"]

    def get_success_url(self):
        return reverse("users:detail")

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields['geo'].label = 'Dein Kiez'
        form.fields['geo'].help_text = 'Bitte zoom an deinen Kiez heran. Dann klicke links auf den Marker und setze in die Gegend, für die du dich verantwortlich fühlst.'
        form.fields['geo'].widget = KiezWidget()
        return form


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


def link_login(request, user_id, secret, url):
    if request.user.is_authenticated:
        if request.user.id != int(user_id):
            messages.add_message(
                request, messages.INFO,
                'Du bist schon eingeloggt!'
            )
        return redirect(url)

    user = get_object_or_404(get_user_model(), pk=int(user_id))
    if user.check_autologin_secret(secret):
        if not user.is_active:
            # Confirm user account (link came from email)
            user.is_active = True
            user.save()
        login(request, user)
        return redirect(url)

    return redirect(url)
