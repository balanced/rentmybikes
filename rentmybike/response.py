from __future__ import unicode_literals
import logging

from flask import session, Response, request, current_app

from rentmybike import renderer


logger = logging.getLogger(__name__)


def render(template_name, request, status_code=None, **template_vars):
    template_vars['request'] = request
    template_vars['session'] = session
    template_vars['config'] = current_app.config
    current_app.update_template_context(template_vars)
    body = renderer.render(template_name, **template_vars)

    if status_code is None:
        if request.method == 'POST':
            status_code = 201
        elif request.method == 'DELETE':
            status_code = 204
        else:
            status_code = 200

    return Response(body, status=status_code)
