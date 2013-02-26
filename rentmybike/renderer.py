from __future__ import unicode_literals

from mako.lookup import TemplateLookup

from rentmybike import config


template_config = config['TEMPLATES']
template_lookup = TemplateLookup(
    directories=template_config['DIRS'],
    module_directory=template_config['TMP_DIR'],
    input_encoding=template_config.get('input_encoding', 'utf-8'),
    output_encoding=template_config.get('output_encoding', 'utf-8'),
    format_exceptions=template_config.get('format_exceptions', True),
    default_filters=['escape'],
    imports=[
        'from flask import url_for',
        'from flask import get_flashed_messages',
        'from markupsafe import escape_silent as escape',
        ],
)


def render(template_location, **kwargs):
    return template_lookup.get_template(
        template_location).render_unicode(**kwargs)
