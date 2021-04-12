import pdb
import sys
import time
import traceback
import simplejson as json
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
import uuid
import logging

logger = logging.getLogger('kn_middleware_logger')

CLEANSED_SUBSTITUTE = '********************'


class KnLogging(MiddlewareMixin):
    """
    In charge of logging events and speed of views, names urls specified in sewttings

    """

    @staticmethod
    def shall_log(request, namespace=None, url_name=None):
        from . import app_settings
        resolver = resolve(request.path)
        namespace = resolver.namespace
        url_name = resolver.view_name

        patterns = app_settings.KN_LOGGING_URL_PATTERNS
        # pdb.set_trace()
        check_url_name = f'{namespace}:{url_name}' if namespace else url_name
        if check_url_name in patterns:
            return True
        elif f'{namespace}:*' in patterns:
            return True
        return False

    def __init__(self, get_response=None):
        self.get_response = get_response
        from .app_settings import KN_LOGGING_URL_PATTERNS
        self.patterns = KN_LOGGING_URL_PATTERNS
        self.start = None
        super(KnLogging, self).__init__(get_response)
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.kn_default_log_id = str(uuid.uuid4())
        self.start = time.time()
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        if self.shall_log(request):

            # if True:
            # Request info
            data = self.get_data(request, response)
            try:
                outbound_payload = json.loads(response.content)
            except:
                pass

            if response.status_code in [200, 301, 302]:
                logger.info(
                    f'{request.path} took {data["response_duration"]} seconds, response: {response.status_code}',
                    extra=data)
        return response

    def get_data(self, request, response=None, exception=None):
        status_code = response.status_code if response else '500'
        content = response.content if response else ''

        data = dict(
            request_id=request.kn_default_log_id,
            method=request.method,
            path=request.path[:255],
            ip=request.META.get('REMOTE_ADDR', ''),
            user=request.user if request.user.is_authenticated else None,
            status_code=status_code,
            outbound_payload=content,
            response_duration=time.time() - self.start,
            post_parameters=self.get_post_parameters(request, request.method),
            meta=request.META
        )
        return data

    def get_post_parameters(self, request, method='POST'):
        """
        Copy of `django/views/debug.py SafeExceptionReporterFilter.get_post_parameters
        Replace the values of POST parameters marked as sensitive with
        stars (*********).
        """
        if request is None or method in ['OPTIONS']:
            return {}
        else:
            sensitive_post_parameters = getattr(request, 'sensitive_post_parameters', [])
            if method == "PUT":
                method_attr = json.loads(getattr(request, "body", b"{}"))
            else:
                method_attr = getattr(request, method, None)
            
            if not method_attr:
                return {}
            cleansed = method_attr.copy()
            if sensitive_post_parameters:
                if sensitive_post_parameters == '__ALL__':
                    # Cleanse all parameters.
                    for k in cleansed:
                        cleansed[k] = CLEANSED_SUBSTITUTE
                    return cleansed
                else:
                    # Cleanse only the specified parameters.
                    for param in sensitive_post_parameters:
                        if param in cleansed:
                            cleansed[param] = CLEANSED_SUBSTITUTE
                    return cleansed
            else:
                return cleansed

    def process_exception(self, request, exception):
        data = self.get_data(request, exception=exception)
        traceback_ = traceback.format_exc()
        logger.error(f'Internal server error Path f{request.path}, Trace{traceback_}', exc_info=sys.exc_info(),
                     extra=data)
