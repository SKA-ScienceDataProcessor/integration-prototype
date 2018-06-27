# -*- coding: utf-8 -*-
"""."""
import jinja2


def render_compose_template(template, **kwargs):
    """Render a docker compose template."""
    template = jinja2.Template(template)
    return template.render(kwargs)
