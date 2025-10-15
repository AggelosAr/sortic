import os
import sys
import importlib.util
import importlib.metadata
from typing import TypeAlias
from collections import defaultdict

# Get list of third-party packages installed via pip
try:
    pip_modules = {dist.metadata['Name'].lower() for dist in importlib.metadata.distributions()}
except Exception:
    pip_modules = set()

def classify_module(module_name: str) -> str:
    """Classify a module as 'builtin', 'stdlib', 'thirdparty', 'local', or 'unknown'."""
    try:
        top_module = module_name.split('.')[0]
        spec = importlib.util.find_spec(top_module)
        if spec is None or spec.origin is None:
            return "unknown"
        if spec.origin == 'built-in':
            return "builtin"
        if top_module.lower() in pip_modules:
            return "thirdparty"
        stdlib_path = os.path.dirname(os.__file__)
        if spec.origin.startswith(stdlib_path):
            return "stdlib"
        return "local"
    except Exception:
        return "unknown"

ModuleToF: TypeAlias = dict[str, list[tuple[str, str | None]]]

IS_IMPORT_LINE = lambda line: line.strip().startswith('import ') or (
    line.strip().startswith('from ') and ' import ' in line)

CLEAN_FIELD = lambda field: field.strip()

class Imports:
    collected_imports: ModuleToF = defaultdict(list)

    # Categories
    cat_local = defaultdict(list)
    cat_stdlib = defaultdict(list)
    cat_builtin = defaultdict(list)
    cat_thirdparty = defaultdict(list)
    cat_unknown = defaultdict(list)

    code = []

    def collect_imports(self, from_file) -> None:
        with open(os.path.join(os.getcwd(), from_file)) as fp:
            lines = fp.readlines()

        for line in lines:
            if IS_IMPORT_LINE(line):
                stripped = line.strip().rstrip()
                if stripped.startswith('from '):
                    parts = stripped[len('from '):].split('import')
                    if len(parts) == 2:
                        module = CLEAN_FIELD(parts[0])
                        names = [name.strip() for name in parts[1].split(',')]
                        for name in names:
                            if ' as ' in name:
                                original, alias = map(str.strip, name.split(' as '))
                                self.collected_imports[module].append((original, alias))
                            else:
                                self.collected_imports[module].append((name, None))
                elif stripped.startswith('import '):
                    names = [name.strip() for name in stripped[len('import '):].split(',')]
                    for name in names:
                        if ' as ' in name:
                            module, alias = map(str.strip, name.split(' as '))
                            self.collected_imports[module].append((None, alias))
                        else:
                            self.collected_imports[name].append((None, None))
            else:
                self.code.append(line)

    def sort_imports(self):
        for module in self.collected_imports:
            category = classify_module(module)
            print(f'MODULE: {module:<20} → {category}')
            if category == 'local':
                self.cat_local[module] = self.collected_imports[module]
            elif category == 'stdlib':
                self.cat_stdlib[module] = self.collected_imports[module]
            elif category == 'builtin':
                self.cat_builtin[module] = self.collected_imports[module]
            elif category == 'thirdparty':
                self.cat_thirdparty[module] = self.collected_imports[module]
            else:
                self.cat_unknown[module] = self.collected_imports[module]

    def v_code(self, to_file):
        with open(os.path.join(os.getcwd(), to_file), 'w') as fo:
            for cat in [self.cat_local, self.cat_stdlib, self.cat_builtin, self.cat_thirdparty, self.cat_unknown]:
                for module, items in self.sortss(cat).items():
                    formatted_imports = []
                    for item in items:
                        if item[0] is None:
                            if item[1]:
                                fo.write(f'import {module} as {item[1]}\n')
                            else:
                                fo.write(f'import {module}\n')
                            break
                        else:
                            if item[1]:
                                formatted_imports.append(f"{item[0]} as {item[1]}")
                            else:
                                formatted_imports.append(item[0])
                    else:
                        if formatted_imports:
                            fo.write(f'from {module} import {", ".join(formatted_imports)}\n')
                fo.write('\n')

            for code_line in self.code:
                fo.write(code_line)

    def sortss(self, dd: ModuleToF):
        sorted_items = sorted(dd.items(), key=lambda item: (not bool(item[1]), len(item[0]), item[0].lower()))
        return {
            module: sorted(
                list({(name, alias) for name, alias in items}),  # deduplicate here
                key=lambda x: (len(x[0] or module), (x[0] or module).lower())
            )
            for module, items in sorted_items
        }


# --- RUN ---
import_solver = Imports()
import_solver.collect_imports(from_file='22.py')  # your input Python file
import_solver.sort_imports()
import_solver.v_code(to_file='22.py')  # output will be written here
