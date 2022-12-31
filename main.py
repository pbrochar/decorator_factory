from typing import Any

from decorator_factory import (
    DecoratedFunction,
    DecoratorArgument,
    DecoratorFolder,
    decorator_factory,
)


def int_validator(nb: int):
    if nb < 10:
        return False
    return True


@decorator_factory()
def repeat(
    func=DecoratedFunction(),
    nb: int = DecoratorArgument(
        default_value=3, validate_type=True, validator=int_validator
    ),
    x: str = DecoratorArgument(default_value="coucou", validate_type=True),
    **kwargs
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


@repeat(nb=3, x="toto", test="coucou")
def print_coucou():
    print("coucou")


r = DecoratorFolder()
r.add(repeat)


@r.repeat
def print_test():
    print("test")


if __name__ == "__main__":
    print_coucou()
    print_test()
