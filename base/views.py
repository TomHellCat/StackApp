from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .forms import SearchForm

from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import caches
from .utils import Red
import time
import datetime
import requests
import json

def home(request):
    per_min = 5 #number of searches per minute
    per_day = 100 #number of searches per day
    if request.method == 'POST':
        if(request.session.get('min_time')==None):
            request.session['min_time'] = datetime.datetime.now().strftime("%m:%d:%Y:%H:%M:%S")
        if(request.session.get('day_time')==None):
            request.session['day_time'] = datetime.datetime.now().strftime("%m:%d:%Y:%H:%M:%S")

        min_time = datetime.datetime.strptime(request.session.get('min_time'), "%m:%d:%Y:%H:%M:%S")
        day_time = datetime.datetime.strptime(request.session.get('day_time'), "%m:%d:%Y:%H:%M:%S")

        current_time = datetime.datetime.now()
        min_timedelta = current_time-min_time
        day_timedelta = current_time-day_time
        vis_in_min = request.session.get('vis_in_min', 0)
        vis_in_day = request.session.get('vis_in_day', 0)

        if(min_timedelta.total_seconds() / 60 >= 1):
            request.session['vis_in_min'] = 1
            request.session['min_time'] = datetime.datetime.now().strftime("%m:%d:%Y:%H:%M:%S")
        else:
            request.session['vis_in_min'] = vis_in_min + 1

        if(day_timedelta.total_seconds() / 60 >= 24*60):
            request.session['vis_in_day'] = 1
            request.session['day_time'] = datetime.datetime.now().strftime("%m:%d:%Y:%H:%M:%S")
        else:
            request.session['vis_in_day'] = vis_in_day  + 1

        if( vis_in_day > per_day or vis_in_min > per_min):   
            return HttpResponse('<h1>Quota exceeded</h1>')
        

        form = SearchForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            title = form.cleaned_data['title']
            url = '/result'
            url = url+'/'+tag+'/'+title
            return redirect(url)
    form = SearchForm()
    return render(request, 'base/home.html', {'form':form})


def result(request,pk1,pk2):
    key = pk1+'_'+pk2
    cached_data = Red.get(key)
    if(cached_data == None):
        cached_data = fillLink(pk1, pk2)
    list1 = []
    for data in cached_data:
        a_dict = {'author':'','score':'','title':'','link':''}
        a_dict['author'] = data[0]
        a_dict['score'] = data[1]
        a_dict['title'] = data[2]
        a_dict['link'] = data[3]
        list1.append(a_dict)

    paginator = Paginator(list1,5)
    page_number = request.GET.get('page')
    list_obj = paginator.get_page(page_number)
    return render(request, 'base/result.html',{'list1':list_obj})

def fillLink(tagged, title):
    temp_list = []
    BASEURL = f'https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=activity&tagged={tagged}&title={title}&site=stackoverflow'
    r = requests.get(BASEURL) 
    r_json = r.json()
    result = r_json['items']
    for i in result:
        temp = []
        temp.append(i['owner']['display_name'])
        temp.append(i['score'])
        temp.append(i['title'])
        temp.append(i['link'])
        temp_list.append(temp)
    key = tagged+'_'+title
    Red.set(key,temp_list)
    return temp_list