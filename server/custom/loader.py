import importlib
import inspect
import pkgutil
import os
import systems.utils

'''
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
'''

'''
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
'''

# returns all objects of same base class as whatever inserted
cached = {}
def load_custom_object(object):
    if type(object).__name__ in cached:
        return cached[type(object).__name__]

    systems.utils.debug_print(f'Loading in replacements for {type(object).__name__} classes')
    
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

    cached[type(object).__name__] = classes
    return classes


# returns the first class that fits 
def compare_replace(object):
    OBJECTS = load_custom_object(object)
    for custom_object in OBJECTS:
        if custom_object.compare_replace(object):
            return custom_object
    return type(object)


