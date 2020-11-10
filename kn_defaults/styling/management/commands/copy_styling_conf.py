# Here we need a command which copies configs from templates/ to project's root
# preferable to copy all of them by default but have an option to exclude any.
# Settings themselves are not final, we should discuss them.
import os
from contextlib import closing

from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import render_to_string

TEMPLATES_NAMES = [
    ".eslintrc.yml",
    ".flake8",
    ".isort.cfg",
    ".pre-commit-config.yaml",
    ".prettierrc.yml"
]


class Command(BaseCommand):

    def handle(self, *args, **options):
        base_dir = getattr(settings, "BASE_DIR", None)
        if not base_dir:
            raise ValueError("`BASE_DIR` is not set")
        for name in TEMPLATES_NAMES:
            with closing(open(os.path.join(base_dir, "..", name), "w")) as fp:
                fp.write(render_to_string(f"kn_styling/{name}"))
