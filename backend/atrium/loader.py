import importlib
import pkgutil

from atrium.command import Command as BaseCommand
import atrium.commands


def load_commands() -> dict[str, BaseCommand]:
    commands: dict[str, BaseCommand] = {}
    prefix = atrium.commands.__name__ + "."

    for module_info in pkgutil.walk_packages(atrium.commands.__path__, prefix):
        if module_info.ispkg:
            continue

        module = importlib.import_module(module_info.name)
        command_class = getattr(module, "Command", None)

        if not command_class or not issubclass(command_class, BaseCommand):
            continue

        command = command_class()
        if not command.type:
            continue

        if command.type in commands:
            raise RuntimeError(f"duplicate command type: {command.type}")

        commands[command.type] = command

    return commands
