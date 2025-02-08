#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

logger = logging.getLogger('logger')

def some_view(request):
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    logger.info("服务已启动")
    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        logger.error(str(exc))
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
