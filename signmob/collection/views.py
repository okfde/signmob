from django.urls import reverse
from django.views.generic import (
    ListView, DetailView, CreateView, FormView, TemplateView
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
    GroupSignupForm,
    CollectionLocationForm, CollectionLocationOrderForm,
    CollectionLocationReportForm,
    CollectionEventJoinForm
)
from .signals import event_left
from .utils import get_period


class HomeView(TemplateView):
    template_name = 'collection/home.html'


class CollectionGroupListView(ListView):
    model = CollectionGroup


class CollectionGroupDetailView(DetailView):
    model = CollectionGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['events'] = CollectionEvent.objects.filter(
            group=self.object,
            event_occurence__end__gte=now
        ).order_by('event_occurence__start')

        user = self.request.user
        if user.is_authenticated:
            is_member = CollectionGroupMember.objects.filter(
                group=self.object,
                user=user
            ).exists()

            context['is_member'] = is_member
        else:
            context['signup_form'] = GroupSignupForm()

        context['members'] = self.object.collectiongroupmember_set.all()
        context['member_count'] = context['members'].count()

        if self.object.calendar:
            context['date'] = now
            context['period'] = get_period(self.object.calendar)

        return context


def join_group(request, pk):
    group = get_object_or_404(CollectionGroup, pk=pk)

    if request.user.is_authenticated:
        if not group.has_member(request.user):
            CollectionGroupMember.objects.create(
                group=group,
                user=request.user
            )
        return redirect(group)

    form = GroupSignupForm(request.POST)
    if form.is_valid():
        user = form.save(request, group)
        messages.add_message(
            request, messages.SUCCESS,
            'Vielen Dank! Bitte bestätige Deine E-Mail-Adresse.'
        )
        try:
            return complete_signup(
                request, user,
                'optional',
                group.get_absolute_url())
        except ImmediateHttpResponse as e:
            return e.response
        return redirect(group)

    return render(
        request,
        'collection/collectiongroup_detail.html',
        {'signup_form': form}
    )


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

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR,
            'Bitte gib alle notwendigen Informationen an.'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('collection:home')


class CollectionLocationOrderView(CreateView):
    template_name = 'collection/collectionlocation_order.html'
    model = CollectionLocation
    form_class = CollectionLocationOrderForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(self.request)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Vielen Dank! Wir senden Dir ein Paket so schnell wie möglich zu!'
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR,
            'Bitte gib alle notwendigen Informationen an.'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('collection:collectionlocation-order-thanks')


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


class CollectionEventJoinView(FormView):
    template_name = 'collection/collectionevent_join.html'
    form_class = CollectionEventJoinForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['members'] = context['object'].collectioneventmember_set.all()
        if context['object'].group:
            context['is_group_member'] = bool(self.request.user in (
                m.user for m in context['object'].group.collectiongroupmember_set.all()
            ))
            if context['object'].group.calendar:
                context['date'] = timezone.now()
                context['period'] = get_period(context['object'].group.calendar)
        if self.request.user.is_authenticated:
            context['first_time'] = CollectionEventMember.objects.filter(
                user=self.request.user
            ).count() < 2
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

    event_left.send(
        sender=CollectionEventMember,
        event=event_member.event,
        user=request.user
    )

    return response
