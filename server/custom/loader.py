import importlib
import inspect
import pkgutil


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


def compare_replace_room(room):
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
