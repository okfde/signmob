from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import (
    CollectionGroup, CollectionGroupMember, CollectionEvent
)
from .forms import GroupSignupForm


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
    CollectionGroupMember.objects.create(
        group=group,
        user=request.user
    )
    return redirect(group)
