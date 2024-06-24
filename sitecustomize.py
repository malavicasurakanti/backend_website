import os
import sys

def patch_graphene_imports():
    graphene_dir = os.path.join(sys.prefix, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'graphene')
    field_file_path = os.path.join(graphene_dir, 'types', 'field.py')
    connection_file_path = os.path.join(graphene_dir, 'relay', 'connection.py')

    replacements = {
        'from collections import Mapping, OrderedDict': 'from collections.abc import Mapping\nfrom collections import OrderedDict',
        'from collections import Iterable, OrderedDict': 'from collections.abc import Iterable\nfrom collections import OrderedDict'
    }

    for file_path in [field_file_path, connection_file_path]:
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            for old, new in replacements.items():
                content = content.replace(old, new)
            with open(file_path, 'w') as file:
                file.write(content)
            print(f"Updated the import statements in {file_path}")
        else:
            print(f"File not found: {file_path}")

patch_graphene_imports()
