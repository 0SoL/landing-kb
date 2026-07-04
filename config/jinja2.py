from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.translation import gettext, ngettext, get_language
from datetime import datetime
import jinja2


def environment(**options):
    extensions = list(options.pop('extensions', []))
    if 'jinja2.ext.i18n' not in extensions:
        extensions.append('jinja2.ext.i18n')
    options['extensions'] = extensions

    env = jinja2.Environment(**options)

    # Install Django's per-thread translation callables so _() responds to
    # LocaleMiddleware's language activation on each request.
    env.install_gettext_callables(gettext, ngettext, newstyle=True)

    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url,
        'now': datetime.now,
        'get_language': get_language,
        'alternate_url': alternate_url,
    })
    return env


def url(name, **kwargs):
    return reverse(name, kwargs=kwargs)


def alternate_url(request, lang):
    """Return the absolute URL of the current page switched to the given language."""
    from django.conf import settings
    path = request.path
    # With prefix_default_language=True all paths start with /<lang>/
    for code, _ in settings.LANGUAGES:
        prefix = f'/{code}/'
        if path.startswith(prefix):
            return request.build_absolute_uri(f'/{lang}/' + path[len(prefix):])
    return request.build_absolute_uri(f'/{lang}/')
