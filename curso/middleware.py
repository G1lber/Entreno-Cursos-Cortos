class DisableCacheMiddleware:
    """
    Middleware para desactivar el cache de páginas sensibles
    cuando el usuario está autenticado.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Si el usuario está autenticado, desactiva cache
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
