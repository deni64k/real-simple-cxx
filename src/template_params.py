from .common import *


def run():
    in_wrappers = [
        ('template_params.adoc', 't'),
        ('template_params_forward.adoc', 'std::forward<T>(t)'),
        ('template_params_move.adoc', 'std::move(t)'),
    ]
    for fname, in_wrapper in in_wrappers:
        print("Generating %s..." % fname)
        with open(os.path.join(DOCS_ROOT, fname), 'w') as out:
            for chunk in async_format(run_wrapped(in_wrapper=in_wrapper)):
                out.write(chunk)

def run_wrapped(*, in_wrapper):
    def probe(*, macros):
        try:
            res = compile_and_run('template_params.cxx', macros=macros)
            return "%s\n" % mcols(res)
        except subprocess.CalledProcessError as e:
            output = str(e.output, 'utf-8')
            return "3+|%s\n" % format_error(output)

    def fn():
        PARAM_TYPES = [
            'T',
            'T const',
            'T *',
            'T const *',
            'T const * const',
            'T &',
            'T const &',
            'T &&',
            'T const &&',
            ]

        yield """
:sourcedir: {SRC_ROOT}

= Type deduction in template arguments

----
include::{{sourcedir}}/template_params.cxx[]
----

""".format(**globals())
        for param_type in PARAM_TYPES:
            yield """
.{param_type}
[cols="2,2,2,3",options="header"]
|=========================================================
|Argument type, {in_wrapper}
|Template parameter type, T
|Template value type, dectype(t)
|\\\\__func__
""".format(**locals())
            for init_clause, in_type in IN_TYPES:
                yield "|%s\n" % in_type
                macros = [
                    '-DINIT_CLAUSE=%s' % init_clause,
                    '-DIN_TYPE=%s' % in_type,
                    '-DIN_WRAPPER(T, t)=%s' % in_wrapper,
                    '-DPARAM_TYPE=%s' % param_type,
                ]

                yield Call(probe, macros=macros)

            yield "|=========================================================\n"

    return fn
