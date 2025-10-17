from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.management import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = "Send example hello email"

    def handle(self, *args, **options):
        self.stdout.write("Send complex email")

        name = "John Smith"
        subject = f"Welcome, {name}"
        context = {
            "name": name,
        }
        # First, render the plain text content.
        text_content = render_to_string(
            template_name="email_newsletters/welcome_message.txt",
            context=context,
        )
        # Secondly, render the HTML content.
        html_content = render_to_string(
            template_name="email_newsletters/welcome_message.html",
            context=context,
        )
        sender = "admin@admin.com"
        recipient = "John@example.com"
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=sender,
            to=[recipient],
            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )

        # Lastly, attach the HTML content to the email instance and send.
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        self.stdout.write(self.style.SUCCESS("Complex email sent"))




