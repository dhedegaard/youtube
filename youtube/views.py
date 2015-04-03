from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from .models import Video, Channel
from .forms import AddChannelForm


def index(request):
    return render(request, 'youtube/index.html', {
        'videos': Video.objects.prefetch_related('uploader').all(),
    })


@login_required
def admin(request):
    if request.method == 'POST':
        form = AddChannelForm(request.POST)
    else:
        form = AddChannelForm()
    return render(request, 'youtube/admin.html', {
        'channels': Channel.objects.order_by('title'),
        'form': form,
    })


@require_POST
@login_required
def channel_delete(request, channelid):
    channel = get_object_or_404(Channel, pk=channelid)
    title = channel.title
    channel.delete()
    messages.success(request, format_html(
        u'Channel with the title removed: <b>{0}</b>',
        title))
    return redirect('admin')


@require_POST
@login_required
def channel_add(request):
    form = AddChannelForm(request.POST)

    if not form.is_valid():
        return admin(request)

    channel = Channel.objects.create(author=form.cleaned_data['channel'])
    channel.update_channel_info()
    channel.fetch_videos()

    messages.success(request, format_html(
        u'Added channel under name <b>{0}</b>',
        channel.title))

    return redirect('admin')
