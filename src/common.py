from pathlib import Path
import concurrent.futures
import os
import os.path
import subprocess
import sys
import tempfile

SRC_ROOT  = os.path.abspath(os.path.join(os.getcwd(), 'src'))
DOCS_ROOT = os.path.abspath(os.path.join(os.getcwd(), 'docs'))

IN_LITERAL = '''IN_TYPE in_val = 0;'''
IN_REF     = '''int val;
IN_TYPE in_val = val;'''

IN_TYPES = [
    (IN_LITERAL, 'int'),
    (IN_LITERAL, 'int const'),
    (IN_LITERAL, 'int *'),
    (IN_LITERAL, 'int const *'),
    (IN_LITERAL, 'int const * const'),
    (IN_REF,     'int &'),
    (IN_REF,     'int const &'),
    (IN_LITERAL, 'int &&'),
    (IN_LITERAL, 'int const &&'),
]

CXX      = os.getenv('CXX', 'g++')
CXXFLAGS = os.getenv('CXXFLAGS', None)
CCACHE   = os.getenv('CCACHE', 'ccache')

CXXFLAGS = CXXFLAGS.splitwords() if CXXFLAGS else []
CXXFLAGS = ['-std=c++17'] + CXXFLAGS
COMPILER = [CCACHE, CXX, *CXXFLAGS]

def run(cmd, *args, **kwargs):
    print('run:', list(map(str, cmd)), file=sys.stderr)
    return subprocess.check_output(cmd, *args, **kwargs)

def compile_and_run(fname_cxx, macros=[]):
    with tempfile.TemporaryDirectory(prefix=fname_cxx) as dtemp:
        fname_obj = os.path.join(dtemp, Path(fname_cxx).with_suffix('.o'))
        fname_exe = os.path.join(dtemp, Path(fname_cxx).with_suffix(''))
        
        run([*COMPILER, os.path.join(SRC_ROOT, fname_cxx), '-c', '-o', fname_obj, *macros],
                stderr=subprocess.STDOUT)
        run([*COMPILER, fname_obj, '-o', fname_exe],
                stderr=subprocess.STDOUT)

        res = subprocess.check_output(fname_exe, shell=True)
        return str(res, 'utf-8')

def format_error(msgs):
    prefix = "error: "
    for msg in msgs.splitlines():
        pos = msg.find(prefix)
        if pos < 0:
            continue
        return bquote(msg[pos + len(prefix):])
    return bquote(msgs)

def mcols(s):
    return '|' + '|'.join(['`' + x + '`' for x in s[1:].split('|')])

def bquote(s):
    return s.replace('\'', '`')

class Call():
    def __init__(self, fn, *args, **kwargs):
        self.fn     = fn
        self.args   = args
        self.kwargs = kwargs

    def __call__(self):
        return self.fn(*self.args, **self.kwargs)

def async_format(generator):
    def itself(x):
        return x

    fs = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*2) as executor:
        for chunk in generator():
            if callable(chunk):
                fs.append(executor.submit(chunk))
            else:
                fs.append(executor.submit(itself, chunk))
        for f in fs:
            yield f.result()
