""" Small lib for adding running zenity commands """

import subprocess
import shutil
from collections import namedtuple

class ZenityBase():
    """ Base class for creating zenity dialogs """

    def __init__(self, dialog, start=True, **kwargs):
        self.history = []
        self.options = kwargs
        try:
            self.options['window-icon'] = self.options.pop('window_icon')
        except KeyError:
            pass

        assert any([x in dialog for x in
                    ['calendar', 'entry', 'info', 'file-selection', 'list',
                     'notification', 'progress', 'question', 'warning',
                     'scale', 'text-info', 'color-selection', 'password',
                     'forms']])

        self.cmd = [shutil.which('zenity'), f'--{dialog}']
        if start:
            self.run()

    def parse(self):
        """ Parse options for command line """
        for option, value in self.options.items():
            self.cmd.extend([f'--{option}', value])

    def run(self):
        """ Run zenity process with specified options """
        self.parse()
        self.process = subprocess.Popen(self.cmd,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def stop(self):
        """ Stop zenity process """

        self.process.terminate()

    @property
    def result(self):
        """ Get the stdout response from zenity """
        return self.read()
    
    def read(self):
        """ Get the stdout response from zenity """
        line = self.process.stdout.readline().decode('UTF-8').strip()
        self.history += [line]
        return line

class Info(ZenityBase):
    """ Display information dialog """

    def __init__(self, **kwargs):
        self.dialog = 'info'
        super().__init__(self.dialog, **kwargs)

class Warn(ZenityBase):
    """ Display warning dialog """

    def __init__(self, **kwargs):
        self.dialog = 'warning'
        super().__init__(self.dialog, **kwargs)

class Question(ZenityBase):
    """ Display question dialog """

    def __init__(self, **kwargs):
        self.dialog = 'question'
        super().__init__(self.dialog, **kwargs)

class Error(ZenityBase):
    """ Display error dialog """

    def __init__(self, **kwargs):
        self.dialog = 'error'
        super().__init__(self.dialog, **kwargs)

class Progress(ZenityBase):
    """ Display progress dialog """

    def __init__(self, **kwargs):
        self.dialog = 'progress'
        self._progress = 0
        super().__init__(self.dialog, **kwargs)

    @property
    def progress(self):
        """ Return current progress """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """ Updates current progress """
        self.process.stdin.write(bytes(str(progress) + '\n', 'UTF-8'))
        self.process.stdin.flush()
        self._progress = progress
        if progress == 100:
            self.stop()

class Input(ZenityBase):
    """ Display input dialog """

    def __init__(self, **kwargs):
        self.dialog = 'entry'
        super().__init__(self.dialog, **kwargs)

class FileSelect(ZenityBase):
    """ Display file selection dialog """

    def __init__(self, **kwargs):
        self.dialog = 'file-selection'
        super().__init__(self.dialog, **kwargs)

class Notification(ZenityBase):
    """ Display notification """

    def __init__(self, **kwargs):
        self.dialog = 'notification'
        super().__init__(self.dialog, **kwargs)

class Scale(ZenityBase):
    """ Scale dialog """

    def __init__(self, **kwargs):
        self.dialog = 'scale'
        kwargs.setdefault('value', '0')
        kwargs.setdefault('min_value', '0')
        kwargs.setdefault('max_value', '100')
        kwargs.setdefault('step', '1')
        kwargs['min-value'] = kwargs.pop('min_value')
        kwargs['max-value'] = kwargs.pop('max_value')
        try:
            kwargs['print-partial'] = kwargs.pop('print_partial')
        except KeyError:
            pass
        try:
            kwargs['hide-value'] = kwargs.pop('hide_value')
        except KeyError:
            pass
        super().__init__(self.dialog, **kwargs)

class Calendar(ZenityBase):
    """ Calendar dialog """

    def __init__(self, **kwargs):
        self.dialog = 'calendar'
        try:
            kwargs['date-format'] = kwargs.pop('date_format')
        except KeyError:
            pass
        super().__init__(self.dialog, **kwargs)

class List(ZenityBase):
    """ List dialog """

    def __init__(self, items, **kwargs):
        self.dialog = 'list'
        self.items = items
        self.columns = []
        try:
            kwargs['print-column'] = kwargs.pop('print_column')
        except KeyError:
            pass

        super().__init__(self.dialog, **kwargs)

    def parse(self):
        """ Parse options for commandl line """
        #TODO: validate lengths of dictionaries are same
        for option, value in self.options.items():
            self.cmd.extend([f'--{option}', value])

        for item in self.items:
            print(item)
            for key in item.keys():
                if key not in self.columns:
                    self.cmd.extend(['--column', key])
                    self.columns.append(key)

            for value in item.values():
                self.cmd.extend([value])

class Color(ZenityBase):
    """ Color dialog, returns Rgb named tuple """

    def __init__(self, **kwargs):
        self.dialog = 'color-selection'
        super().__init__(self.dialog, **kwargs)

    @property
    def result(self):
        """ Returns an rgb tuple """
        values = self.read()[4:-1].split(',')
        colors = ['red', 'green', 'blue']
        Rgb = namedtuple('Rgb', colors)
        try:
            return Rgb(*[int(x) for x in values])
        except ValueError:
            return None

class Password(ZenityBase):
    """ Password dialog """
    #TODO: handle | in password
    def __init__(self, **kwargs):
        self.dialog = 'password'
        try:
            if kwargs['username']:
                kwargs['username'] = ''
                self._username = True
            else:
                del kwargs['username']
                self._username = False
        except KeyError:
            self._username = False
        super().__init__(self.dialog, **kwargs)

    @property
    def result(self):
        """ Returns an Auth named tuple with username and password """

        Auth = namedtuple('Auth', ['username', 'password'])
        password_string = self.read()
        if not self._username:
            return Auth(username=None, password=password_string)
        username, password = password_string.split('|')
        return Auth(username=username, password=password)

class Text(ZenityBase):
    """ Text dialog """

    def __init__(self, **kwargs):
        self.dialog = 'text-info'
        try:
            if kwargs['editable']:
                kwargs['editable'] = ''
            else:
                del kwargs['editable']
        except KeyError:
            pass

        try:
            if kwargs['html']:
                kwargs['html'] = ''
            else:
                del kwargs['html']
        except KeyError:
            pass
        super().__init__(self.dialog, **kwargs)

class FormPart():
    """ Part of a form """

    def __init__(self, formtype, text):
        assert any([x in formtype for x in ['entry', 'password', 'calendar']])
        self.formtype = formtype
        self.arg = f'--add-{formtype}'
        self.text = text

class Form(ZenityBase):
    """ Form dialog """

    def __init__(self, parts, **kwargs):
        self.dialog = 'forms'
        self.parts = parts
        try:
            self.options['print-column'] = self.options.pop('print_column')
        except KeyError:
            pass
        super().__init__(self.dialog, **kwargs)

    def parse(self):
        """ Parse options for command line """

        for option, value in self.options.items():
            self.cmd.extend([f'--{option}', value])

        for part in self.parts:
            self.cmd.extend([part.arg, part.text])

    @property
    def result(self):
        """ Returns a dictionary of form parts and inputs """

        keys = [x.text for x in self.parts]
        values = self.read().split('|')
        return {k:v for k, v in zip(keys, values)}
