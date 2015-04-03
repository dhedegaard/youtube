from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Video


def index(request):
    return render(request, 'youtube/index.html', {
        'videos': Video.objects.prefetch_related('uploader').all(),
    })


@login_required
def admin(request):
    return render(request, 'youtube/admin.html', {
        'videos': Video.objects.prefetch_related('uploader').all(),
    })
