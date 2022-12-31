from functools import wraps, partial
from typing import Dict, List, Callable, Optional, Any
from .errors import ConflictNameError


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
        validator: Optional[Callable] = None
    ) -> None:

        self.default_value = default_value
        self.validate_type = validate_type
        self._value = self.default_value

        self._arg_name = None

        self._type = type

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
        return {arg.arg_name:arg for arg in self.arguments}

    def _get_args(self):
        return {arg.arg_name:arg.value for arg in self.arguments}
    
    def _set_args(self, **kwargs):
        for key, value in kwargs.items():
            self.arg_getter.get(key).value = value

    def get_decorated_args(self, **kwargs):
        self._set_args(**kwargs)
        return self._get_args()


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

    def __call__(
        self, func: Optional[Callable] = None, *args: Any, **kwargs: Any
    ) -> Any:

        if not func:
            return partial(self.__call__, *args, **kwargs)
        else:
            self.decorated.func = func

        updated_parameters = self.arguments.get_decorated_args(**kwargs)

        @wraps(self.decorated.func)
        def wrapper(*args: Any, **kwargs: Any):
            self.decorated.args = args
            self.decorated.kwargs = kwargs

            if self.auto_return:
                self.decorator(**updated_parameters)
                return self.decorated.result
            else:
                return self.decorator(**updated_parameters)

        return wrapper
