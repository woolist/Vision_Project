from django.shortcuts import render
import io
from PIL import Image as im
import torch

from django.shortcuts import render
from django.views.generic.edit import CreateView

def landing(request):
   return render(
       request,
       'dashboard/landing.html'
   )




