import os
import json

from importlib import import_module

from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect

from lazysignup.decorators import allow_lazy_user

from django.http import JsonResponse

from users.serializers import UserSerializer, RequestSerializer, CurveSerializer
from users.models import Request, Curve
from django.views.generic import View, DetailView

User = get_user_model()

def index(request):
    content = ""
    #--------
    # * APIとして利用する際には上側を使用
    #--------
    # return JsonResponse(UserSerializer(request.user).data, status=200)

    #--------
    # frontend として使用する際には下側を使用
    #--------
    # ROOT_DOMAIN = "herokuapp.com" if os.environ.get("STAGE") == "alpha" else "emonotate.com"
    module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
    queries = [f'{query}={request.GET[query]}' for query in request.GET]
    if not request.user.is_authenticated:
        return redirect(f"{module.APPLICATION_URL}app/login/{'' if not request.GET else '?' + '&'.join(queries)}")
    return redirect(module.APPLICATION_URL)


@login_required
def app(request):
    context = {
        'permissions': json.dumps(list(request.user.get_all_permissions())),
        'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY')
    }

    template = 'backend/app.html'
    return render(request, template, context)


class FreeHandView(View):
    def get(self, request, *args, **kwargs):
        curve_json = Curve.get_empty_json()
        if "request" in request.GET:
            req = Request.objects.get(pk=int(request.GET.get("request")))
            video_id = req.content.youtubecontent.video_id
            curve_json["content"] = req.content.id
            curve_json["value_type"] = req.value_type.id
            curve_json["user"] = request.user.id
            curve_json["locked"] = True
            curve_json["room_name"] = req.room_name
            request_json = RequestSerializer(req).data
            context = {
                "option": "new",
                "video_id": video_id,
                "has_google_form": req.google_form != None,
                "request_model": req,
                "curve_json": json.dumps(curve_json),
                "request_json": json.dumps(request_json)
            }
            template = 'backend/free-hand.html'
        else:
            video_id = request.GET.get("video_id")
            curve_json["content"] = None
            curve_json["value_type"] = 1
            curve_json["user"] = request.user.id
            curve_json["locked"] = True
            curve_json["room_name"] = request.GET.get("room_name", 
                f"{request.GET.get('room_name')}")
            context = {
                "option": "new",
                "video_id": video_id,
                "curve_json": json.dumps(curve_json),
                "request_json": {}
            }
            template = 'backend/free-hand.html'
        response = render(request, template, context)
        response.set_cookie('GCP_ACCESS_TOKEN', 'value')
        return response


class FreeHandDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        curve = Curve.objects.get(pk=pk)
        curve_dict = CurveSerializer(curve).data
        context = {
            "option": "detail",
            "video_id": curve.content.youtubecontent.video_id,
            "curve_json": json.dumps(curve_dict),
            "request_json": {}
        }
        template = 'backend/free-hand.html'
        response = render(request, template, context)
        response.set_cookie('GCP_ACCESS_TOKEN', 'value')
        return response


class FoldLineView(View):
    def get(self, request, *args, **kwargs):
        curve_json = Curve.get_empty_json()
        if "request" in request.GET:
            req = Request.objects.get(pk=int(request.GET.get("request")))
            video_id = req.content.youtubecontent.video_id
            curve_json["content"] = req.content.id
            curve_json["value_type"] = req.value_type.id
            curve_json["values"] = req.values
            curve_json["user"] = request.user.id
            curve_json["locked"] = True
            curve_json["room_name"] = req.room_name
            request_json = RequestSerializer(req).data
            context = {
                "video_id": video_id,
                "has_google_form": req.google_form != None,
                "request_model": req,
                "curve_json": json.dumps(curve_json),
                "request_json": json.dumps(request_json)
            }
            template = 'backend/fold-line.html'
        else:
            video_id = request.GET.get("video_id")
            curve_json["value_type"] = 1
            curve_json["user"] = request.user.id
            curve_json["locked"] = request.GET.get("locked", False)
            curve_json["room_name"] = request.GET.get("room_name", 
                f"{request.GET.get('room_name')}")
            context = {
                "video_id": video_id,
                "curve_json": json.dumps(curve_json)
            }
            template = 'backend/fold-line.html'
        response = render(request, template, context)
        response.set_cookie('GCP_ACCESS_TOKEN', 'value')
        return response


class FoldLineDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        curve = Curve.objects.get(pk=pk)
        context = {
            "video_id": curve.content.youtubecontent.video_id,
            "curve_json": CurveSerializer(curve).data,
            "request_json": {}
        }
        template = 'backend/free-hand.html'
        response = render(request, template, context)
        response.set_cookie('GCP_ACCESS_TOKEN', 'value')
        return response
