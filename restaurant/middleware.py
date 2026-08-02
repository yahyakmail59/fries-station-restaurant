from django.conf import settings


class SiteNoIndexMiddleware:
    """Keep staging responses out of search indexes, including non-HTML files."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.SITE_NOINDEX:
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return response
