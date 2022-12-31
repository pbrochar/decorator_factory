from functools import wraps, partial
from typing import Dict, List, Callable, Optional, Any
import functools

class DecoratedFunction:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self._func = None

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, func):
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.result = self.func(*args, *self.args, **kwargs, **self.kwargs)
        return self.result


class DecoratorArgument:
    def __init__(
        self,
        default_value: Optional[Any],
        type: Optional[type] = None,
        validate_type: Optional[bool] = False,
        validator: Optional[Callable] = None,
    ) -> None:

        self.default_value = default_value
        self.validate_type = validate_type
        self._type = type
        self._value = None

        self.value = self.default_value

        self._arg_name = None

        self.validator = validator

    @property
    def arg_name(self):
        return self._arg_name

    @arg_name.setter
    def arg_name(self, arg_name):
        if not self._arg_name:
            self._arg_name = arg_name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        if not self.type:
            self._type = type
        self.type_validator()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.type_validator()

    @staticmethod
    def _is_same_type(type_a, type_b):
        return type_a == type_b or type_a == Any or type_b == Any

    def type_validator(self):
        if self.validate_type and self.value and self.type:
            value_type = type(self.value)
            if not self._is_same_type(value_type, self.type):
                raise TypeError(f"{value_type} != {self.type} for {self.arg_name}")


class DecoratorArguments:
    def __init__(self, arguments: List[DecoratorArgument]) -> None:
        self.arguments = arguments
        self.arg_getter = self._set_getter()

    def _set_getter(self):
        return {arg.arg_name: arg for arg in self.arguments}

    def _get_args(self, **kwargs):
        if kwargs:
            arguments = {arg.arg_name: arg.value for arg in self.arguments}
            arguments.update(kwargs)
            return arguments
        else:
            return {arg.arg_name: arg.value for arg in self.arguments}

    def _set_args(self, **kwargs):
        for key, value in kwargs.items():
            try:
                self.arg_getter.get(key).value = value
            except AttributeError:
                pass

    def get_decorated_args(self, **kwargs):
        self._set_args(**kwargs)
        return self._get_args(**kwargs)


class DecoratorFactory:
    def __init__(
        self,
        arguments: DecoratorArguments,
        decorated: DecoratedFunction,
        decorator: Callable,
        auto_return: bool,
    ) -> None:

        self.arguments = arguments
        self.decorated = decorated
        self.decorator = decorator
        self.auto_return = auto_return
        functools.update_wrapper(self, self.decorator)

    def __call__(
        self, func: Optional[Callable] = None, *args: Any, **kwargs: Any
    ) -> Any:

        if not func:
            return partial(self.__call__, *args, **kwargs)
        else:
            self.decorated.func = func
        decorator_parameters = self.arguments.get_decorated_args(**kwargs)

        @wraps(self.decorated.func)
        def wrapper(*args: Any, **kwargs: Any):
            self.decorated.args = args
            self.decorated.kwargs = kwargs

            if self.auto_return:
                self.decorator(**decorator_parameters)
                return self.decorated.result
            else:
                return self.decorator(**decorator_parameters)

        return wrapper


class DecoratorFolder:
    def __init__(self, decorators=None) -> None:
        self.decorators: List = []

    def add(self, decorator):
        self.decorators.append(decorator)
        setattr(self, decorator.__name__, decorator)

    def remove(self, removed_decorator):
        for index, decorator in enumerate(self.decorators):
            if decorator == removed_decorator:
                self.decorators.pop(index)
                delattr(self, decorator.__name__)
