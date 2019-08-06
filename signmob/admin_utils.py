from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import helpers

from signmob.users.tasks import send_bulk_mail
from signmob.users.models import User


class SendMailMixin():
    def _get_send_mail_user_ids(self, queryset):
        return list(queryset.values_list('id', flat=True))

    def send_mail(self, request, queryset):
        """
        Send mail to users

        """

        user_ids = self._get_send_mail_user_ids(queryset)
        if request.POST.get('subject'):
            subject = request.POST.get('subject', '')
            body = request.POST.get('body', '')
            count = len(user_ids)
            send_bulk_mail.delay(user_ids, subject, body)
            self.message_user(request, _("%d mail tasks queued." % count))
            return None

        emails = User.objects.filter(id__in=user_ids).values_list('email', flat=True)
        emails = ', '.join(emails)

        select_across = request.POST.get('select_across', '0') == '1'
        context = {
            'opts': self.model._meta,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'queryset': queryset,
            'select_across': select_across,
            'mail_count': len(self._get_send_mail_user_ids(queryset)),
            'emails': emails
        }

        # Display the confirmation page
        return TemplateResponse(request, 'admin_utils/send_mail.html', context)
    send_mail.short_description = _("Send mail to users")
