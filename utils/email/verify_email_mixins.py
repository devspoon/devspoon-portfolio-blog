import hashlib
import uuid
from datetime import timedelta
from pickle import TRUE
from typing import NoReturn, Tuple, Union

# from minitutorial import settings
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

# from django.core.mail import send_mail
from utils.email.async_send_email import send_mail


class VerifyEmailMixin:
    email_template_name_generator_token = "/email/registration_verification.html"
    email_template_name_custom_token = "/email/verification.html"
    token_generator = default_token_generator

    def send_verification_email_management(
        self, template: str, from_email: str, user: object, token_gen_type: int = 1
    ) -> dict[str, Union[int, str]]:
        if token_gen_type == 1:
            if template is not None:
                self.email_template_name_generator_token = template

            return self.__create_verification_email_generator_token(from_email, user)
        else:
            if template is not None:
                self.email_template_name_custom_token = template

            return self.__create_verification_email_custom_token(from_email, user)

    def __create_verification_email_generator_token(
        self, from_email: str, user: object
    ) -> dict[str, Union[int, str]]:
        result = {}
        result["token"] = self.token_generator.make_token(user)
        url = self.__build_verification_link(result["token"])
        subject = "Congratulations on becoming a member."
        message = "Go to the following link to verify. {}".format(url)
        msg_html = render(
            self.request,
            settings.TEMPLATE_DIR + self.email_template_name_generator_token,
            {"url": url},
        ).content.decode("utf-8")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=msg_html,
            fail_silently=False,
        )
        result["sending_mail_num"] = 1
        return result

    def __build_verification_link(self, token: str) -> str:
        return "{}{}{}".format(
            self.request.META.get("HTTP_ORIGIN"),
            reverse("users:verification_email"),
            "?key=" + token,
        )

    def __create_email_key(self, user_id) -> str:
        random_key = str(uuid.uuid4())
        sha_data = hashlib.sha256()
        sha_data.update(str(user_id).encode("utf-8"))
        hash_key = sha_data.hexdigest()

        return random_key[::2] + hash_key[::2]

    def __create_verification_email_custom_token(
        self, from_email: str, user: object
    ) -> dict[str, Union[int, str]]:
        result = {}
        result["token"] = self.__create_email_key(user.id)
        link = (
            "http://"
            + self.request.get_host()
            + reverse("users:verification_email")
            + "?key="
            + result["token"]
        )

        email_context = {"link": link}

        msg_plain = render_to_string(
            settings.TEMPLATE_DIR
            + self.email_template_name_custom_token.replace(".html", ".txt"),
            email_context,
        )
        msg_html = render_to_string(
            settings.TEMPLATE_DIR + self.email_template_name_custom_token, email_context
        )

        subject = (
            "Congratulations on becoming a member. Go to the following link to verify."
        )

        send_mail(
            subject=subject,
            message=msg_plain,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=msg_html,
            fail_silently=False,
        )
        result["sending_mail_num"] = 1
        return result

    def reset_password_management(
        self, template: str, from_email: str, user: object
    ) -> dict[str, Union[int, str]]:
        return self.__create_reset_password_verification_generator_token(
            from_email, user, template
        )

    def __create_reset_password_verification_generator_token(
        self, from_email: str, user: object, template: str
    ) -> dict[str, Union[int, str]]:
        result = {}
        result["token"] = self.token_generator.make_token(user)
        url = self.__build_verification_link(result["token"])
        subject = "You can change your password."
        message = "Go to the following link to verify. {}".format(url)
        msg_html = render(
            self.request, settings.TEMPLATE_DIR + template, {"url": url}
        ).content.decode("utf-8")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=msg_html,
            fail_silently=False,
        )
        result["sending_mail_num"] = 1
        return result
