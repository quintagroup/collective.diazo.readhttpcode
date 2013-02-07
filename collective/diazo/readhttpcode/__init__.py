from diazo.utils import quote_param
from diazo.wsgi import DiazoMiddleware, XSLTMiddleware
from lxml import etree
from repoze.xmliter.serializer import XMLSerializer
from repoze.xmliter.utils import getHTMLSerializer
from webob import Request


class ExtendedXSLTMiddleware(XSLTMiddleware):
    """Apply XSLT in middleware
    """
    def __call__(self, environ, start_response):
        request = Request(environ)
        if self.should_ignore(request):
            return self.app(environ, start_response)

        if self.remove_conditional_headers:
            request.remove_conditional_headers()
        else:
            # Always remove Range and Accept-Encoding headers
            request.remove_conditional_headers(
                remove_encoding=True,
                remove_range=False,
                remove_match=False,
                remove_modified=True,
            )

        response = request.get_response(self.app)

        if not self.should_transform(response):
            return response(environ, start_response)
        try:
            input_encoding = response.charset

            # Note, the Content-Length header will not be set
            if request.method == 'HEAD':
                self.reset_headers(response)
                return response(environ, start_response)

            # Prepare the serializer
            try:
                serializer = getHTMLSerializer(response.app_iter,
                                               encoding=input_encoding)
            except etree.XMLSyntaxError:
                # Abort transform on syntax error for empty response
                # Headers should be left intact
                return response(environ, start_response)
        finally:
            if hasattr(response.app_iter, 'close'):
                response.app_iter.close()

        self.reset_headers(response)

        # Set up parameters

        params = {}
        for key, value in self.environ_param_map.items():
            if key in environ:
                if value in self.unquoted_params:
                    params[value] = environ[key]
                else:
                    params[value] = quote_param(environ[key])
        for key, value in self.params.items():
            if key in self.unquoted_params:
                params[key] = value
            else:
                params[key] = quote_param(value)
        params['httpcode'] = quote_param(str(response.status_int))

        # Apply the transformation
        tree = self.transform(serializer.tree, **params)

        # Set content type (normally inferred from stylesheet)
        # Unfortunately lxml does not expose docinfo.mediaType
        if self.content_type is None:
            if tree.getroot().tag == 'html':
                response.content_type = 'text/html'
            else:
                response.content_type = 'text/xml'
        response.charset = tree.docinfo.encoding or self.charset

        # Return a repoze.xmliter XMLSerializer, which helps avoid re-parsing
        # the content tree in later middleware stages.
        response.app_iter = XMLSerializer(tree, doctype=self.doctype)

        # Calculate the content length - we still return the parsed tree
        # so that other middleware could avoid having to re-parse, even if
        # we take a hit on serialising here
        if self.update_content_length:
            response.content_length = len(str(response.app_iter))

        return response(environ, start_response)


class ExtendedDiazoMiddleware(DiazoMiddleware):
    def get_transform_middleware(self):
        return ExtendedXSLTMiddleware(self.app, self.global_conf,
                                      tree=self.compile_theme(),
                                      read_network=self.read_network,
                                      read_file=self.read_file,
                                      update_content_length=self.update_content_length,
                                      ignored_extensions=self.ignored_extensions,
                                      environ_param_map=self.environ_param_map,
                                      doctype=self.doctype,
                                      content_type=self.content_type,
                                      unquoted_params=self.unquoted_params,
                                      **self.params)
