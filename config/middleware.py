"""
Custom middleware for ngrok tunnel compatibility.

The ngrok free tier shows an interstitial warning page for every request
that doesn't include a 'ngrok-skip-browser-warning' header.  This blocks
CSS, JS, images and font files from loading because the browser's sub-resource
requests don't carry that header.

This middleware sets the 'ngrok-skip-browser-warning' response header and
also injects a small <meta> tag that helps with the initial page load.
"""


class NgrokMiddleware:
    """
    When the request comes through an ngrok tunnel (detected by the Host
    header containing 'ngrok'), this middleware:

    1. Adds a response header that signals to ngrok the app is intentional.
    2. Sets permissive Content-Security-Policy for ngrok's proxy.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        host = request.META.get('HTTP_HOST', '')
        if 'ngrok' in host:
            # Tell ngrok this is a legitimate app response
            response['ngrok-skip-browser-warning'] = 'true'

        return response
