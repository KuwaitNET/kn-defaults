from django.conf import settings
from django.core.checks import Error, register

try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze


@register()
def check_pre_commit(app_configs, **kwargs):
    errors = []
    installed = False

    for package in freeze.freeze():
        if package.startswith("pre-commit"):
            installed = True
            break

    if not installed and not settings.DEBUG:
        errors.append(
            Error('`pre-commit` must be installed in python PATH',
                  obj='settings',
                  id='kn_defaults.E004',
                  )
        )

    return errors
