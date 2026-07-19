import importlib
import inspect
import pkgutil
import os


def load_customs_all(path):
    classes = []

    package_name = path
    package = importlib.import_module(package_name)

    # Iterate over all modules in custom/rooms
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_module_name)

        # Find all classes in the module
        for _, obj in inspect.getmembers(module, inspect.isclass):
            classes.append(obj)

    return classes



def load_customs(path, object):
    classes = []

    package_name = path
    package = importlib.import_module(package_name)

    # Iterate over all modules in custom/rooms
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_module_name)

        # Find all classes in the module
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == full_module_name and issubclass(obj, type(object)):
                classes.append(obj)

    return classes


# returns all objects of same base class as whatever inserted
def load_custom_object(object):
    path = "custom"
    classes = []

    package = importlib.import_module(path)
    root = package.__path__[0]

    for dirpath, _, filenames in os.walk(root):
        # Skip the root custom directory itself
        if dirpath == root:
            continue

        for filename in filenames:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue

            module_name = (
                os.path.relpath(os.path.join(dirpath, filename), root)
                .replace(os.sep, ".")
                .removesuffix(".py")
            )

            full_module_name = f"{path}.{module_name}"

            module = importlib.import_module(full_module_name)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == full_module_name and issubclass(obj, type(object)):
                    classes.append(obj)

    return classes

'''
def compare_replace_rooms(room):
    ROOMS = load_customs("custom.rooms", room)
    for custom_room in ROOMS:
        if custom_room.compare_replace(room):
            return custom_room
    return type(room)

def compare_replace_npcs(npc):
    NPCS = load_customs("custom.npcs", npc)
    for custom_npc in NPCS:
        if custom_npc.compare_replace(npc):
            return custom_npc
    return type(npc)

def compare_replace_items(item):
    ITEMS = load_customs("custom.items", item)
    for custom_item in ITEMS:
        if custom_item.compare_replace(item):
            return custom_item
    return type(item)
'''

# returns the first class that fits 
def compare_replace(object):
    OBJECTS = load_custom_object(object)
    for custom_object in OBJECTS:
        if custom_object.compare_replace(object):
            return custom_object
    return type(object)


