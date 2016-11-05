import os
import subprocess

import itertools
from django.utils.html import escape
from django.http.response import StreamingHttpResponse
from django.views import View

def stream_command_output_git():
    return itertools.chain(stream_command_output('git pull'), '---', stream_command_output('git status'))

def stream_command_output(command):
    yield "<pre>"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        out = process.stdout.read(1024).decode("utf-8")
        if out == '' and process.poll() != None:
            break
        if out != '':
            yield escape(out)
    process.kill()
    yield "</pre>"


class ReloadView(View):
    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(stream_command_output('supervisorctl restart webinfret'))

class SelfDeployView(View):
    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(
            itertools.chain(stream_command_output('git pull'), '---', stream_command_output('git status'), '---', stream_command_output('supervisorctl restart webinfret'))
        )
