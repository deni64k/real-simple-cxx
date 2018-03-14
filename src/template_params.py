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
            run_wrapped(out, in_wrapper=in_wrapper)

def run_wrapped(out, *, in_wrapper):
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

    print("""
:sourcedir: {SRC_ROOT}

= Type deduction in template arguments

Rule of thumb:


----
include::{{sourcedir}}/template_params.cxx[]
----

""".format(**globals()), file=out)
    for param_type in PARAM_TYPES:
        print("""
.{param_type}
[cols="2,2,2,3",options="header"]
|=========================================================
|Argument type, {in_wrapper}
|Template parameter type, T
|Template value type, dectype(t)
|\\\\__func__""".format(**locals()), file=out)
        for init_clause, in_type in IN_TYPES:
            print("|%s" % in_type, file=out)
            macros = [
                '-DINIT_CLAUSE=%s' % init_clause,
                '-DIN_TYPE=%s' % in_type,
                '-DIN_WRAPPER(T, t)=%s' % in_wrapper,
                '-DPARAM_TYPE=%s' % param_type,
            ]

            try:
                res = compile_and_run('template_params.cxx', macros=macros)
                res = mcols(res)
                print("%s" % res, file=out)
            except subprocess.CalledProcessError as e:
                output = str(e.output, 'utf-8')
                print("3+|%s" % format_error(output), file=out)

        print("|=========================================================", file=out)
