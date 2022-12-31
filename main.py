from decorator_factory import decorator_factory, DecoratorArgument, DecoratedFunction
from typing import Any


@decorator_factory()
def repeat(
    func = DecoratedFunction(),
    nb: int = DecoratorArgument(default_value=3, validate_type=True),
    x: str = DecoratorArgument(default_value=3, validate_type=True)

):
    """
    Parameters
    ----------
      nb: int
    """
    for _ in range(nb):
        ret = func()
    print(x)
    return ret


@repeat(nb=3, x='toto')
def print_coucou():
    print('coucou')

if __name__ == "__main__":
    print_coucou()