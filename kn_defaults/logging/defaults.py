from functools import wraps
import logging
import os

logger = logging.getLogger('default')

KN_FORMATTER = "%(levelname)s:%(name)s; " \
               "REQ_id:%(request_id)s; %(message)s; path=%(path)s; method=%(method)s;ip=%(ip)s; " \
               "status_code:%(status_code)%; response_duration:%(response_duration)s; " \
               "post_parameters: %(post_parameters)s; outbound:%(outbound_payload)s"
FUNCTION_LOGGER_FORMATTER = '{levelname}:{message} - args={func_args} kwargs={func_kwargs} return={func_return_value} '
BASE_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose_kn': {
            'format': KN_FORMATTER,
        },
        'verbose_project': {
            'format': '{levelname}:{message} - LocalVars={vars} ',
            'style': '{',
        },
        'verbose_functions': {
            'format': FUNCTION_LOGGER_FORMATTER,
            'style': '{',
        }
    },
    'handlers': {
        'kn_default_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose_project'
        },
        'file_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.getcwd(), 'log.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose_project',
        },
        'functions_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.getcwd(), 'log.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose_functions',
        },
    },
    'loggers': {
        'kn_defaults': {
            'handlers': ['kn_default_handler'],
            'level': 'INFO',
        },
        'default': {
            'handlers': ['file_log'],
            'level': 'DEBUG',
        },
        'kn_function_logger': {
            'handlers': ['file_log'],
            'level': 'DEBUG',
        }
    }
}


def log(level, msg, collect_localvars=True, exc_info=None, extra=None, stack_info=False):
    import inspect
    extra = extra or {}
    vars = {}
    caller_name = ''
    if collect_localvars:
        frame = inspect.currentframe()
        calframe = inspect.getouterframes(frame, 2)
        try:
            vars = frame.f_back.f_locals
            caller_name = calframe[1][3]

        finally:
            del frame

    extra['vars'] = vars
    extra['caller_name'] = vars

    logger.log(level, msg, exc_info=exc_info, extra=extra, stack_info=stack_info)


def logging_decorator(func, *, level=10, msg=''):
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        logger = logging.getLogger('kn_function_logger')
        message = msg or func.__name__
        # print("Hi, " + func.__name__ + " returns:")

        return_value = func(*args, **kwargs)
        logger.log(level, message, extra={'func_args': args, 'func_kwargs': kwargs, 'func_return_value': return_value})
        return return_value

    return function_wrapper
