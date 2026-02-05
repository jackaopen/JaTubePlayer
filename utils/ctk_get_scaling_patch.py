from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker
import sys,wsgiref.util
def _apply_google_auth_patch():
    """
    make the redirectly html page show success message instead of just blank page.
    """
    from google_auth_oauthlib.flow import _RedirectWSGIApp
    def new___call__(self, environ, start_response):
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode("utf-8")]
    _RedirectWSGIApp.__call__ = new___call__

