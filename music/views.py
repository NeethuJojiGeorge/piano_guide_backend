from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from music.models import Song
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from .handle_recording import handle_recording
from .algo.process_music import process_music
import time

def index(request):
    return HttpResponse("Hello, world. You're at the music index.")


def songs(request):
    data = Song.objects.all()
    data_json = serializers.serialize('json', data)
    return HttpResponse(data_json, content_type='application/json')


@csrf_exempt
def upload(request):
    if request.method == 'POST':
        # This is the starting time of the first note calculated at the front-end
        start_time = float(request.POST.get('start_time'))
        print("#"*5 + " Start Time from user request: ", start_time)
        # This is the selected BPM
        bpm = float(request.POST.get('bpm'))
        print("#"*5 + " BPM from user request: ", bpm)
        # This is the name of the song
        song_name = request.POST.get('song_name')
        print("-------------song_name received: ", song_name)
        # Store the uploaded recording at /media/audios
        path = handle_recording(request.FILES['recording'])

        # time.sleep(3)
        print("-----------------path of the recording: ", path)

        '''
        for testing
        '''
        fileName = "/home/neethu/Downloads/wrong10C4.m4a"
        path = fileName

        # note_result is array, overall_report is dictionary, for scores
        note_result, overall_report = process_music(path, start_time, bpm, song_name)
        
        if not note_result and not overall_report:
            res = "no sound detected"
            response = HttpResponse(res, status=400)
            return response

        #  an array of 0 or 1, where 0 indicates the note is correct, 1 indicates it has wrong frequency,
        #  2 indicates it's omitted, 3 indicates 多弹, 4 indicates it has wrong rhythm, 5 "Wrong" indicates both wrong beat and wrong freq
        #  the length of the array should be the total number of notes in the piece, 62 for Ode to Joy.
        data = []
        for i in note_result:
            if i == "True":
                data.append(0)
            elif i == "WrongFreq":
                data.append(1)
            elif i == "Miss":
                data.append(2)
            elif i == "Dup":
                data.append(3)
            elif i == "WrongBeat":
                data.append(4)
            elif i == "Wrong":
                data.append(5)
            else:
                data.append(0)
        """
        data = []
        for i in range(62):
            if i == 2:
                data.append(2)
            elif i == 5:
                data.append(3)
            elif i == 10:
                data.append(4)
            else:
                data.append(1)
        """
        res = {}
        res['bpm'] = round(overall_report["speed"], 1)
        res['speed'] = round(overall_report["speed_score"], 3)
        res['note'] = round(overall_report["freq_accuracy"], 3)
        res['rhythm'] = round(overall_report["beat_accuracy"], 3)
        print(res['rhythm'])
        res["overall"] = overall_report["correctness"]
        res['data'] = data
        # res = {'bpm': 120, 'speed': 0.8, 'note': 0.9, 'rhythm': 0.7, 'overall': 0.9, 'data': data}
        response = JsonResponse(res, safe=False)
        return HttpResponse(response, content_type='application/json')
    return HttpResponse("Something wrong", content_type="text/plain")
