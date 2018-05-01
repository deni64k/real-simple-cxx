from .common import *

import os
import re


def run():
    fname = os.path.join(DOCS_ROOT, 'auto.adoc')
    print("Generating %s..." % fname)
    with open(fname, 'w') as out:
        for chunk in async_format(auto):
            out.write(chunk)

def auto():
    AUTO_TYPES = [
        'auto',
        'auto const',
        'auto *',
        'auto const *',
        'auto const * const',
        'auto &',
        'auto const &',
        'auto &&',
        'auto const &&',
    ]

    def probe(init_clause, in_type, auto_type):
        macros = [
            '-DINIT_CLAUSE=%s' % init_clause,
            '-DIN_TYPE=%s' % in_type,
            '-DAUTO=%s' % auto_type,
        ]
            
        try:
            res = compile_and_run('auto.cxx', macros=macros)
            return mcols(res)
        except subprocess.CalledProcessError as e:
            res = str(e.output, 'utf-8')
            return "3+|%s\n" % format_error(res)

    yield """
:sourcedir: {SRC_ROOT}

= Type deduction in auto and decltype(auto)

== Rule of thumb:

==== auto
Gives you a brand new _copy_ of your variable ignoring all _cvr qualifiers_ until you specify them explicitly.

==== decltype(auto) and decltype(expr)
Gives a variable with the _same type_ as `expr` including _cvr qualifiers_.

==== decltype\\((expr))
As `decltype(expr)` but always gives a _reference_.

== Experiment

----
include::{{sourcedir}}/auto.cxx[]
----

""".format(**globals())
    for init_clause, in_type in IN_TYPES:
        yield """
[cols="<3,^2,<3,<3,<3",options="header"]
|===
3+<|Type of `in_val` is `{in_type}`
<|`decltype(in_val)` result
<|`decltype\\((in_val))` result
""".format(**locals())
        for auto_type in AUTO_TYPES:
            yield "|`%s`\n|[small,gray]#= in_val =>#\n" % auto_type
            yield Call(probe, init_clause, in_type, auto_type)
        yield "|===\n"
