from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.admin import helpers
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class SendMailMixin():
    def send_mail(self, request, queryset):
        """
        Send mail to users

        """

        # Check that the user has change permission for the actual model
        if not request.user.is_superuser:
            raise PermissionDenied

        if request.POST.get('subject'):
            subject = request.POST.get('subject', '')
            body = request.POST.get('body', '')
            count = queryset.count()
            user_ids = queryset.values_list('id', flat=True)
            send_bulk_mail.delay(user_ids, subject, body)
            self.message_user(request, _("%d mail tasks queued." % count))
            return None

        select_across = request.POST.get('select_across', '0') == '1'
        context = {
            'opts': self.model._meta,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'queryset': queryset,
            'select_across': select_across
        }

        # Display the confirmation page
        return TemplateResponse(request, 'admin_utils/send_mail.html', context)
    send_mail.short_description = _("Send mail to users")
