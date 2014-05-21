class BreadcrumbMiddleware(object):
    def process_response(self, request, response):
        response['toto'] = 'tata'
        return response
