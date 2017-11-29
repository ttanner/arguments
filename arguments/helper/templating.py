# -*- coding: utf-8 -*-

from datetime import datetime
import os
from munch import Munch
from pyjade.ext.jinja import Compiler as JinjaCompiler
from pyjade.ext.jinja import PyJadeExtension as JinjaJadeExtension
from pyjade.utils import process
from werkzeug.datastructures import ImmutableDict


class JinjaAutoescapeCompiler(JinjaCompiler):
    autocloseCode = 'if,for,block,filter,autoescape,with,trans,spaceless,comment,cache,macro,localize,compress,call'.split(',')

    def visitCode(self, code):
        if code.buffer:
            val = code.val.lstrip()
            val = self.var_processor(val)
            self.buf.append('%s%s%s' % (self.variable_start_string, val,
                                        self.variable_end_string))
        else:
            self.buf.append('{%% %s %%}' % code.val)

        if code.block:
            self.visit(code.block)
            if not code.buffer:
                codeTag = code.val.strip().split(' ', 1)[0]
                if codeTag in self.autocloseCode:
                    self.buf.append('{%% end%s %%}' % codeTag)


class PyJadeExtensionForBabel(JinjaJadeExtension):

    def preprocess(self, source, name, filename=None):
        return process(source, filename=name, compiler=JinjaAutoescapeCompiler, **self.options)


class PyJadeExtension(JinjaJadeExtension):

    def preprocess(self, source, name, filename=None):
        if (not name or
                (name and not os.path.splitext(name)[1] in self.file_extensions)):
            return source
        return process(source, filename=name, compiler=JinjaAutoescapeCompiler, **self.options)


def select_jinja_autoescape(filename):
    """Returns `True` if autoescaping should be active for the given
    template name.

    !taken from Flask.
    """
    if filename is None:
        return False
    return filename.endswith(('.html', '.htm', '.xml', '.xhtml', '.jade'))


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def fake_translate(name, *a, **k):
    el = [str(e) for e in [name, a if a else None, list(k.values()) if k else None] if e]
    return ", ".join(el)


def make_jinja_env(jinja_environment_class, jinja_options):
    jinja_globals = dict(url_for=lambda *a, **k: "#",
                         g=Munch(locale="de"),
                         current_user=Munch(is_authenticated=False),
                         _=fake_translate,
                         ngettext=fake_translate,
                         get_flashed_messages=lambda *a, **k: [])

    default_jinja_options = ImmutableDict(
        extensions=[PyJadeExtension, "jinja2.ext.autoescape"],
        autoescape=select_jinja_autoescape
    )

    jinja_env = jinja_environment_class(**default_jinja_options, **jinja_options)
    jinja_env.globals.update(jinja_globals)
    jinja_env.filters['datetimeformat'] = format_datetime
    jinja_env.filters['markdown'] = lambda t: t
    return jinja_env
