# -*- coding: utf-8 -*-
"""."""
# from .generator import
import jinja2


def test_generate():
    """."""
    senders = [dict(position=2), dict(position='foo')]
    template = jinja2.Template(
        'Sender list:\n'
        '{% for sender in senders %}'
        '{{ sender.position }}\n'
        '{% endfor %}'
    )
    print(template.render(senders=senders))


if __name__ == '__main__':
    test_generate()
