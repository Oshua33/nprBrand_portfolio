from contextlib import contextmanager
from email import encoders
from email.mime.base import MIMEBase
import os
import smtplib
from email.mime import multipart, text
from email.utils import formataddr
import ssl
from typing import Optional, List, Union
import pydantic
from nprOlusolaBe.configs import settings as config
from nprOlusolaBe.exceptions import mailException
from nprOlusolaBe.lib.mail import template_finder


class Mailer:

    def __init__(
        self,
        subject: str,
        sender_email: str = config.smtp_username,
        sender_password: str = config.smtp_password,
        email_host: str = config.smtp_host,
        email_server_port: int = config.smtp_port,
        template_folder: Optional[pydantic.DirectoryPath] = config.email_template_dir,
        website_name: str = "Olusola Owonikoko",
        body: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> None:
        """
        Initialize mailer with required configurations.

        Args:
            subject: Email subject
            sender_email: Sender's email address
            sender_password: Sender's email password
            email_host: SMTP host server
            email_server_port: SMTP server port
            template_folder: Path to email templates
            website_name: Name to show as sender
            body: Plain text body (optional)
            template_name: Template file name (optional)
            context: Template context dictionary (optional)
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.template_name = template_name
        self.email_host = email_host
        self.email_server_port = email_server_port
        self.website_name = website_name
        self.body = body
        self.context = context or {}
        self.subject = subject
        self.template_folder = template_folder
        self.attachments: List[MIMEBase] = []

    def add_attachment(self, attachment_paths: List[str]) -> None:
        """
        Add file attachments to the email.

        Args:
            attachment_paths: List of file paths to attach
        """
        for path in attachment_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Attachment not found: {path}")

            try:
                with open(path, "rb") as f:
                    attachment = MIMEBase("application", "octet-stream")
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(path)}",
                    )
                    self.attachments.append(attachment)
            except Exception as e:
                raise mailException.MailException(
                    f"Failed to attach file {path}: {str(e)}"
                )

    @contextmanager
    def _smtp_connection(self):
        """Create an SMTP connection with proper SSL context"""
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(self.email_host, self.email_server_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                yield server
        except ssl.SSLError as e:
            raise mailException.ServerConnectionError(f"SSL Error: {str(e)}")
        except smtplib.SMTPException as e:
            raise mailException.ServerConnectionError(f"SMTP Error: {str(e)}")
        except Exception as e:
            raise mailException.ServerConnectionError(f"Connection failed: {str(e)}")

    def _create_message(
        self, recipient_emails: Union[List[str], str]
    ) -> multipart.MIMEMultipart:
        """Create the email message with all components"""
        message = multipart.MIMEMultipart()
        message["From"] = formataddr((self.website_name, self.sender_email))
        message["Subject"] = self.subject

        if isinstance(recipient_emails, list):
            message["To"] = ", ".join(recipient_emails)
        else:
            message["To"] = recipient_emails

        # Add body content
        if self.template_name and self.template_folder:
            # Implement template rendering logic here
            body_content = self._render_template()
            message.attach(text.MIMEText(body_content, "html"))
        elif self.body:
            message.attach(text.MIMEText(self.body, "plain"))

        else:
            raise mailException.InvalidEmailContentError(
                "Email body content is required"
            )

        # Add attachments
        for attachment in self.attachments:
            message.attach(attachment)

        return message

    def _render_template(self) -> str:
        """Render email template with context"""
        # Implement your template rendering logic here
        # This is a placeholder - replace with your actual template rendering code
        template = template_finder.MailTemplate(
            template_folder=self.template_folder,
        )
        try:
            return template.render(
                context=self.context, template_name=self.template_name
            )
        except template_finder.TemplateFolderNotFoundError:
            raise mailException.TemplateFolderNotFoundError(
                f"Template folder not found: {self.template_folder}"
            )

    def send_mail(self, recipient_emails: Union[List[str], str]) -> None:
        """
        Send email to one or more recipients.

        Args:
            recipient_emails: Single email address or list of email addresses

        Raises:
            InvalidEmailContentError: If no body content is provided
            ServerConnectionError: If connection to mail server fails
            MailException: For other mail-related errors
        """
        message = self._create_message(recipient_emails)

        try:
            with self._smtp_connection() as server:
                server.send_message(message)
        except Exception as e:
            raise mailException.MailException(f"Failed to send email: {str(e)}")
