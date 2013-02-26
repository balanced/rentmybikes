from __future__ import unicode_literals
import logging

from flask import current_app
from flask.ext import mail

from rentmybike import renderer


logger = logging.getLogger(__name__)


class RendereringException(Exception):
    pass


class EmailTemplateRenderer(object):
    def __init__(self, template_location):
        self.template_location = template_location

    def render_email_template(self, **kwargs):
        if not self.template_location:
            raise RendereringException('missing template_location')
        if not self.template_location.startswith('emails/'):
            self.template_location = 'emails/' + self.template_location
        template_vars = {}
        template_vars.update(kwargs)
        return renderer.render(self.template_location, **template_vars)


def send_email(to, subject, template, **kwargs):
    renderer = EmailTemplateRenderer(template)
    content = renderer.render_email_template(**kwargs)
    msg = mail.Message(subject, recipients=[to])
    msg.html = content
    current_app.emailer.send(msg)
