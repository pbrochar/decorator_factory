from functools import wraps, partial
from typing import Dict, List, Callable, Optional, Any
import inspect


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
        self.result = self.func(*args, *self.args, **kwargs, self.kwargs)
        return self.result



class DecoratorArgument:

    def __init__(
        self,
        default_value: Optional[Any],
        arg_name: Optional[str] = None,
        usage_name: Optional[str] = None,
        type: Optional[type] = None,
    ) -> None:
        
        self.default_value = default_value
        self.value = self.default_value

        self._type = type
        self._arg_name = arg_name
        self.usage_name = usage_name

    
    @property
    def arg_name(self):
        return self._arg_name
    
    @arg_name.setter
    def arg_name(self, arg_name):
        if not self.arg_name:
            self.arg_name = arg_name
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, type):
        if not self.type:
            self._type = type


class DecoratorArguments:

    def __init__(self, arguments: List[DecoratorArgument]) -> None:
        self.arguments = arguments
        self.usual_arguments = self._set_usual_arguments()
        self.conversion_arguments = self._get_conversion_argument_mapping()
    

    def _get_conversion_argument_mapping(self) -> Dict[str, str]:
        return {arg.usage_name or arg.arg_name:arg.arg_name for arg in self.arguments}
    
    
    def _set_usual_arguments(self) -> Dict[str,Any]:
        return {arg.arg_name if not arg.usage_name else arg.usage_name:arg.value for arg in self.arguments}
    
    
    def _convert_arguments_names(self) -> Dict[str, Any]:
        return {self.conversion_arguments.get(key):value for key, value in self.usual_arguments.items()}
    
    
    def _update_usual_arguments(self, **kwargs) -> None:
        self.usual_arguments.update(kwargs)
    

    def get_decorated_args(self, **kwargs):
        self._update_usual_arguments(**kwargs)
        return self._convert_arguments_names()
    

class DecoratorFactory:

    def __init__(
        self, 
        arguments: DecoratorArguments, 
        decorated: DecoratedFunction, 
        decorator: Callable,
        auto_return: bool
    ) -> None:

        self.arguments = arguments
        self.decorated = decorated
        self.decorator = decorator
        self.auto_return = auto_return
    
    def __call__(
        self, 
        func: Optional[Callable] = None, 
        *args: Any, 
        **kwargs: Any
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
        
        return DecoratorFactory(
            arguments=DecoratorArguments(argument),
            decorated=decorated,
            decorator=func,
            auto_return=auto_return
        )
        
    return inner