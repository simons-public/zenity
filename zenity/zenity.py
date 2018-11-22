""" small lib for adding running zenity commands """

import subprocess
import shutil

class ZenityBase():
    """ Base class for creating zenity dialogs """

    def __init__(self, dialog, start=True, **kwargs):
        assert any([x in kwargs['icon'] for x in
                    ['info', 'warning', 'question', 'error']])
        assert any([x in dialog for x in
                    ['calendar', 'entry', 'info', 'file-selection', 'list',
                     'notification', 'progress', 'question', 'warning',
                     'scale', 'text-info', 'color-selection', 'password',
                     'forms']])

        self.cmd = [shutil.which('zenity'), f'--{dialog}']
        self.options = kwargs
        self.options['window-icon'] = self.options.pop('icon')
        if start:
            self.run()

    def run(self):
        """ Run zenity process with specified options """

        for option, value in self.options.items():
            self.cmd.extend([f'--{option}', value])
        result = subprocess.check_output(self.cmd)
        self.result = str(result)

class Info(ZenityBase):
    """ Display information dialog """

    def __init__(self, **kwargs):
        dialog = 'info'
        kwargs.setdefault('title', 'Information')
        kwargs.setdefault('icon', 'info')
        ZenityBase.__init__(self, dialog, **kwargs)

class Warn(ZenityBase):
    """ Display warning dialog """

    def __init__(self, **kwargs):
        dialog = 'warning'
        kwargs.setdefault('title', 'Warning')
        kwargs.setdefault('icon', 'warning')
        ZenityBase.__init__(self, dialog, **kwargs)
