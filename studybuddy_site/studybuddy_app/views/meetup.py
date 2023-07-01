import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib import messages
from ..forms import MeetupForm
from ..models import Meetup
from studybuddy_app.common.date import date_from_form


# https://docs.djangoproject.com/en/4.2/ref/class-based-views/generic-display/#listview


class IndexView(generic.ListView):
    model = Meetup

    def get_queryset(self):
        return Meetup.objects.filter(
            start_time__gte=timezone.now())

    def post(self, request, *args, **kwargs):
        return create(request)


class DetailView(generic.DetailView):
    model = Meetup

    def post(self, request, *args, **kwargs):
        meetup = self.get_object()
        return update(request, meetup)


def path_meetups_pk(request, pk):
    meetup = get_object_or_404(Meetup, pk=pk)
    if request.method == 'GET':
        return detail(request, meetup)
    elif request.method == 'POST':
        return update(request, meetup)
    elif request.method == 'DELETE':
        return delete(request, meetup)
    raise Http404("Page not found.")


def new(request):
    meetup_form = MeetupForm()
    context = {"meetup": None,
               "meetup_form": meetup_form,
               "http_method": 'POST',
               "action_url": reverse('studybuddy_app:meetup.path_meetups'),
               "button_text": 'Create'
               }
    return render(request, "studybuddy_app/meetup_form.html", context)


def edit(request, pk):
    meetup = get_object_or_404(Meetup, pk=pk)
    return render_meetup_form(request, meetup=meetup, pk=pk)


def render_meetup_form(request, meetup=None, old_meetup_form=None, pk=None):
    if pk is None:
        action_url = reverse('studybuddy_app:meetup.path_meetups')
    else:
        action_url = reverse(
            'studybuddy_app:meetup.path_meetups_pk',
            args=[pk])
        
    if old_meetup_form is None:
        meetup_form = MeetupForm(instance=meetup)
    else:
        meetup_form = old_meetup_form
        
    context = {"meetup": meetup,
               "http_method": 'POST',
               "meetup_form": meetup_form,
               "action_url": action_url,
               "button_text": 'Save'}
    return render(request, "studybuddy_app/meetup_form.html", context)


def save_meetup(meetup_form):
    if not meetup_form.is_valid():
        return None
    meetup = meetup_form.save(commit=False)
    meetup.start_time = date_from_form(meetup.start_time)
    meetup.save()
    return meetup


def create(request):
    # title = request.POST["title"]
    # meetup = Meetup(title=title,
    #                 start_time=timezone.now() + datetime.timedelta(days=1))
    # meetup.save()
    # return HttpResponseRedirect(
    #     reverse("studybuddy_app:meetup.path_meetups_pk",
    #             args=[meetup.id]))
    meetup_form = MeetupForm(request.POST, request.FILES)
    meetup = save_meetup(meetup_form=meetup_form)
    if meetup:
        messages.success(request, ('Your meetup was successfully added!'))

        return HttpResponseRedirect(
            reverse("studybuddy_app:meetup.path_meetups_pk",
                    args=[meetup.id]))
    else:
        messages.error(request, 'Error saving form')
        return render_meetup_form(request, old_meetup_form=meetup_form)


def update(request, meetup):
    meetup_form = MeetupForm(request.POST, instance=meetup)
    meetup = save_meetup(meetup_form=meetup_form)
    if meetup:
        messages.success(request, ('Your meetup was successfully updated!'))
        return render_meetup(request, meetup)
        return HttpResponseRedirect(
            reverse("studybuddy_app:meetup.path_meetups_pk",
                    args=[meetup.id]))
    else:
        messages.error(request, 'Error saving form')
        return render_meetup_form(request, meetup=meetup)


def render_meetup(request, meetup):
    context = {"meetup": meetup}
    return render(request, "studybuddy_app/meetup_detail.html", context)


def detail(request, meetup):
    context = {"meetup": meetup,
               "view": "detail"}
    return render(request, "studybuddy_app/meetup_detail.html", context)


def delete(request, pk):
    meetup = get_object_or_404(Meetup, pk=pk)
    meetup.delete()
    return HttpResponseRedirect(
        reverse("studybuddy_app:meetup.path_meetups"))


def rsvp(request, meetup_id):
    return HttpResponse("You rsvp on meetup %s." % meetup_id)
