from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, FormView, TemplateView
)
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from allauth.account.utils import complete_signup
from allauth.exceptions import ImmediateHttpResponse

from .models import (
    CollectionGroup, CollectionGroupMember, CollectionEvent,
    CollectionLocation, CollectionEventMember
)
from .forms import (
    GroupSignupForm, CollectionLocationForm, CollectionLocationReportForm,
    CollectionEventJoinForm
)
from .utils import get_period


class HomeView(TemplateView):
    template_name = 'collection/home.html'


class CollectionGroupDetailView(DetailView):
    model = CollectionGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = CollectionEvent.objects.filter(group=self.object)

        user = self.request.user
        if user.is_authenticated:
            is_member = CollectionGroupMember.objects.filter(
                group=self.object,
                user=user
            ).exists()

            context['is_member'] = is_member
        else:
            context['signup_form'] = GroupSignupForm(initial={
                'group': self.object
            })

        return context


@login_required
def join_group(request, pk):
    group = get_object_or_404(CollectionGroup, pk=pk)
    if not CollectionGroupMember.objects.filter(
            group=group, user=request.user).exists():
        CollectionGroupMember.objects.create(
            group=group,
            user=request.user
        )
    return redirect(group)


class CollectionLocationCreateView(CreateView):
    model = CollectionLocation
    form_class = CollectionLocationForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(self.request)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Vielen Dank! Der neue Sammelort sollte jetzt auf der Karte erscheinen!'
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('collection:home')


class CollectionLocationReportView(FormView):
    template_name = 'collection/collectionlocation_report.html'
    form_class = CollectionLocationReportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def get_object(self):
        return get_object_or_404(CollectionLocation, pk=self.kwargs['pk'])

    def form_valid(self, form):
        location = self.get_object()

        form.save(location)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Vielen Dank! Es wird sich jemand darum kümmern!'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('collection:home')


class CollectionEventJoinView(LoginRequiredMixin, FormView):
    template_name = 'collection/collectionevent_join.html'
    form_class = CollectionEventJoinForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['members'] = context['object'].collectioneventmember_set.all()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            event=self.get_object()
        )
        return kwargs

    def get_object(self):
        return get_object_or_404(CollectionEvent, pk=self.kwargs['pk'])

    def form_valid(self, form):
        event = self.get_object()

        form.save(self.request.user)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Vielen Dank, dass du dabei bist!'
        )
        return redirect(event)


@login_required
def cancel_event_membership(request, pk):
    event_member = get_object_or_404(
        CollectionEventMember, pk=pk, user=request.user
    )

    response = redirect(event_member.event)
    event_member.delete()

    return response
