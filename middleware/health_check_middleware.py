from django.db import connection

class HealthCheckMiddleware:

    db_status = False 

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not self.db_status:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                self.db_status = True  
            except Exception:
                self.db_status = False
        if self.db_status and request.path == '/health-check/':
            from django.http import JsonResponse
            return JsonResponse({"status": "OK"}, status=200)

        response = self.get_response(request)
        return response