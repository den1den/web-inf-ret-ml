import itertools
import subprocess

from django.http.response import StreamingHttpResponse
from django.utils.html import escape
from django.views import View

from config.config import PHP_MAIN_SCRIPT


def stream_command_output_git():
    return itertools.chain(stream_command_output('git pull'), '---', stream_command_output('git status'))


def stream_command_output(command):
    yield "<pre>"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        out = process.stdout.read(1024).decode("utf-8")
        if out == '' and process.poll() is not None:
            break
        if out != '':
            yield escape(out)
    yield "</pre>"


class TestPhpOutputView(View):
    def get(self, request, *args, **kwargs):
        php_args = 'test_command'
        return StreamingHttpResponse(stream_command_output(PHP_MAIN_SCRIPT + ' ' + php_args))
