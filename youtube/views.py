from django.shortcuts import render

from .models import Video


def index(request):
    return render(request, 'youtube/index.html', {
        'videos': Video.objects.all(),
    })
