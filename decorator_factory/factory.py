import inspect

from .errors import NoFunctionError
from .models import (
    DecoratedFunction,
    DecoratorArgument,
    DecoratorArguments,
    DecoratorFactory,
)


def decorator_factory(auto_return: bool = False):
    def inner(func):
        arguments = []
        decorated = None

        for key, value in inspect.signature(func).parameters.items():
            if isinstance(value.default, DecoratorArgument):
                argument = value.default

                if value.annotation == inspect.Signature.empty and not argument.type:
                    raise ValueError(f"Need type for arg {argument.arg_name}")

                argument.arg_name = key
                argument.type = value.annotation
                arguments.append(argument)

            elif isinstance(value.default, DecoratedFunction):
                decorated = value.default

        if not decorated:
            raise NoFunctionError(func.__name__)

        factory = DecoratorFactory(
            arguments=DecoratorArguments(arguments),
            decorated=decorated,
            decorator=func,
            auto_return=auto_return,
        )

        return factory

    return inner
