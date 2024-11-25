from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from datetime import datetime, timedelta


server_active = False
block_until = None 

@ratelimit(key='ip', rate='1/m', block=True)  
@api_view(['GET'])
def health_check(request):
    global server_active, block_until
    if server_active:
        now = datetime.now()
        if block_until and now < block_until:

            return Response({
                "status": "OK",
                "message": f"Server is already active. Health-check disabled until {block_until}."
            }, status=200)

    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;") 
        server_active = True  
        block_until = datetime.now() + timedelta(minutes=10)  
        return Response({"status": "OK"}, status=200)
    except Exception as e:
        return Response({"status": "ERROR", "details": str(e)}, status=500)