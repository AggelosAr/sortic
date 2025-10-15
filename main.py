from typing import TypeAlias
import json
from functools import *
from itertools import dropwhile
import os
from collections import defaultdict
import requests

# Determines if the current line is an import line
IS_IMPORT_LINE = lambda line: any([ # noqa
                                    line.startswith('import '),
                                    line.startswith('from ') and ' import ' in line]
                                  )


# Removes new line from end of a string
REMOVE_TRAILING_NEW_LINE = lambda line: ''.join(list(dropwhile(lambda el: el == '\n', list(line)[::-1]))[::-1]) # noqa


# Sanitize a lines e.g.
CLEAN_LINES = lambda lines: list(filter(lambda line: line and line != ' ' and line != '\n', lines)) # noqa

# Removes whitespace on 1 field
CLEAN_FIELD = lambda field: field.strip() # noqa

# Removes whitespace on many fields
CLEAN_FIELDS = lambda fields: list(map(CLEAN_FIELD, fields)) # noqa

__SPECIAL__ = [
    "subprocess"
    "\\"
]

ModuleToF: TypeAlias = dict


def builtin_store(func):
    def wrapper():
        import requests

        try:
            with open(os.path.join(os.getcwd(), '___buildins___.txt'), 'r') as fp:
                print("USING CACHED ")
        except FileNotFoundError:
            print("REQUESTING BUILTINS")
            response = requests.get("https://docs.python.org/3/py-modindex.html#cap-_")
            lines = []
            for line in response.text.split('\n'):
                line = line.strip()
                if '<a href="library/' in line:
                    lines.append(line.split('<code class="xref">')[1].split('<')[0])

            with open('___buildins___.txt', 'a') as fp:
                for line in lines:
                    fp.write(line)
                    fp.write(',')
        return func()

    return wrapper


@builtin_store
def find_builtins():
    with open(os.path.join(os.getcwd(), '___buildins___.txt'), 'r') as fp:
        data = fp.readlines()[0]
    return set([f'{el}' for el in data.split(',')])


# Ambitious
# @builtin_store
# def find_PyIndex():
#     with open(os.path.join(os.getcwd(), '___buildins___.txt'), 'r') as fp:
#         data = fp.readlines()[0]
#     return set([f'{el}' for el in data.split(',')])


class Imports:
    sorted_imports: ModuleToF = defaultdict(list)

    collected_imports: ModuleToF = defaultdict(list)

    cat1 = defaultdict(list)
    cat2 = defaultdict(list)
    cat3 = defaultdict(list)

    import_lines = []
    code = []

    def collect_imports(self, from_) -> None:

        with open(os.path.join(os.getcwd(), from_)) as fp:
            pythons = fp.readlines()

        CLEAN_IMPORTS = lambda lines: list(map(REMOVE_TRAILING_NEW_LINE, COLLECT_IMPORTS(lines)))  # noqa

        for python_line in pythons:

            if IS_IMPORT_LINE(python_line):
                python_line = REMOVE_TRAILING_NEW_LINE(python_line)

                if 'from ' in python_line:
                    python_line = python_line[len('from '):]
                    parts = CLEAN_LINES(python_line.split('import'))
                    self.collected_imports[CLEAN_FIELD(parts[0])].extend(CLEAN_FIELDS(parts[1:]))
                else:
                    python_line = python_line[len('import '):]
                    parts = CLEAN_LINES(python_line.split(','))
                    for p in parts:
                        self.collected_imports[CLEAN_FIELD(p)]
            else:
                self.code.append(python_line)

    def sort_imports(self):
        all_buildins = find_builtins()
        for module in self.collected_imports:
            if module in all_buildins:
                self.cat1[module] = self.collected_imports[module]
            # elif module in find_PyIndex:
            #     self.cat2[module] = self.collected_imports[module]
            else:
                self.cat3[module] = self.collected_imports[module]

    def sort_builtins(self):
        res = []
        builtins = find_builtins()

        __subprocess___ = None
        if 'subprocess' in builtins:
            # special handling
            __subprocess___ = builtins.pop('__subprocess___')

        res.extend(builtins.keys)


    def v_code(self, to_):
        with open(os.path.join(os.getcwd(), to_), 'w') as fo:
            for module, packages in self.sortss(self.cat1).items():
                if packages:
                    fo.write(f'from {module} import {', '.join(packages)}')
                else:
                    fo.write(f'import {module}')
                fo.write('\n')

            fo.write('\n')

            for module, packages in self.sortss(self.cat2).items():
                if packages:
                    fo.write(f'from {module} import {', '.join(packages)}')
                else:
                    fo.write(f'import {module}')
                fo.write('\n')

            for module, packages in self.sortss(self.cat3).items():
                if packages:
                    fo.write(f'from {module} import {', '.join(packages)}')
                else:
                    fo.write(f'import {module}')
                fo.write('\n')

            fo.write('\n')

            for code_line in self.code:
                fo.write(code_line)

    def sortss(self, dd):
        sorted_items = sorted(dd.items(), key=lambda item: bool(item[1]))
        return dict(sorted_items)


import_solver = Imports()
import_solver.collect_imports(from_='main.py')
import_solver.sort_imports()
import_solver.v_code(to_='22.py')
