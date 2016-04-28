from django.shortcuts import render
from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.views.generic import View, FormView, TemplateView
from django.conf import settings
from django.core.files import File
from django.core.servers.basehttp import FileWrapper

from fairdata.models import Uploaded_File
import json, csv, time, string, random, sys, subprocess, os, re
import datetime

headers = []

def index(request):
    t = loader.get_template("knightapp/index.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

def accept_file(request):
    # Michael Feldman file_id code
    file_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits*2) for x in range(25))
    file_id += datetime.datetime.now().isoformat()[:19].replace('-','').replace(':','') # Add timestamp
    print request.FILES
    new_uploaded_file = Uploaded_File(uploaded_file=request.FILES["file"], generated_id=file_id)
    new_uploaded_file.save()
    request.FILES["file"].seek(0) # 'Rewind' the file so it can be read in the next section

    file_path = "/home/fair/web/fairness.haverford.edu/live_site/knight" + new_uploaded_file.uploaded_file.url.replace("%20", " ")
    file_reader = csv.reader(open(file_path, 'rU'), delimiter=',')

    rows = []
    for row in file_reader:
        rows.append(row)

    headers = rows[0]
    lines = rows[1:]

    options = []
    for i in range(0,len(headers)):
        options.append([])

    for i in range(0, len(options)):
        for j in range(0, len(lines)):
            if lines[j][i] not in options[i]:
               options[i].append(lines[j][i])

    # DEREK FILE READING STUFF
    return HttpResponse(json.dumps({"valid": True,
                                    "result": {"url": new_uploaded_file.uploaded_file.url,
                                               "id": file_id, "cols": headers, "array_options": options},
                                    }))

def run_script(request):
    in_path = str(request.GET.get('in_path')) + ' '
    protected = str(request.GET.get('protect')) + ' '
    pro_pos = str(request.GET.get('protected_pos')) + ' '
    selected = str(request.GET.get('selected')) + ' '
    sel_pos = str(request.GET.get('selected_pos')) + ' '
    out_path = str(request.GET.get('out_path'))
    command = "python knightapp/main.py " + in_path + protected + pro_pos + selected + sel_pos + out_path + " 2> error.txt > output.txt"

    error_or_nah = "Success!"

#    ls_command = "ls ../media/user_uploads > output.txt"
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        error_or_nah = "Failed to run script!"
        pass
    except OSError:
        error_or_nah = "Failed to run script!"
        pass
#    subprocess.call(ls_command, shell=True)
    return HttpResponse(error_or_nah)
