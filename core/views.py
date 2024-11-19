from django.shortcuts import render

# Create your views here.
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async

async def async_streaming_view(request):
    async def async_stream():
        for i in range(10):
            yield f"Chunk {i}\n"
    return StreamingHttpResponse(async_stream(), content_type="text/plain")