__all__ = ['randargs', 'IntRandomiser', 'FloatRandomiser', 'SelectionRandomiser']

import random
import inspect
from functools import wraps
from typing import Callable, Iterable

from functools import lru_cache


def randargs(log_ignore=None):
    if log_ignore is None:
        log_ignore = []

    def decorator(fn):
        def generate_arguments(value):
            if isinstance(value, ArgumentRandomiser):
                return value()
            elif isinstance(value, Iterable) and not isinstance(value, str):
                return type(value)([generate_arguments(i) for i in value])
            else:
                return value

        def argument_log(d: dict, ignore: list):
            ret = {}
            for k, v in d.items():
                if not k.startswith('_') and k not in ignore:
                    if hasattr(v, '__dict__'):
                        ret[k] = argument_log(v.__dict__, [])
                        ret[k]['_cls'] = v.__class__.__name__
                    else:
                        ret[k] = v
            return ret

        @wraps(fn)
        def wrapper(*args, **kwargs):
            # if args or kwargs contain ArgumentRandomisers, they are called and their return value used instead
            args = [generate_arguments(a) for a in args]
            kwargs = {k: generate_arguments(v) for k, v in kwargs.items()}

            # log the function arguments and store in .call_history and .last_call
            log_kwargs = argument_log(kwargs, log_ignore)

            getattr(wrapper, 'call_history').append(log_kwargs)
            setattr(wrapper, 'last_call', log_kwargs)

            return fn(*args, **kwargs)

        wrapper.call_history = []
        wrapper.last_call = None

        return wrapper

    return decorator


class ArgumentRandomiser(random.Random):
    def __init__(self, *args, **kwargs):
        super().__init__(x=kwargs.get('seed'))

    @staticmethod
    def _make_callable(x):
        if isinstance(x, ArgumentRandomiser):
            return x
        return lambda: x

    def __call__(self):
        raise NotImplementedError

    def __repr__(self):
        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'

    def __getattribute__(self, item):
        ret = super().__getattribute__(item)
        if isinstance(ret, ArgumentRandomiser):
            return ret()
        return ret


class IntRandomiser(ArgumentRandomiser):
    def __init__(self, low, high, size=None, ordered=True, **kwargs):
        self.low = low
        self.high = high
        self.size = size
        self.ordered = ordered
        super().__init__(**kwargs)

    def __call__(self):
        low = self.low
        high = self.high
        size = self.size

        if size is None:
            return self.randint(low, high)

        ret = self.choices(range(low, high + 1), k=size)
        if self.ordered:
            return tuple(sorted(ret)[:: -1 if low > high else 1])
        return tuple(ret)


class FloatRandomiser(ArgumentRandomiser):
    def __init__(self, low, high, size=None, dp=3, ordered=True, **kwargs):
        self.low = low
        self.high = high
        self.size = size
        self.dp = dp
        self.ordered = ordered
        super().__init__(**kwargs)

    def __call__(self):
        low = self.low
        high = self.high
        size = self.size
        dp = self.dp

        if size is None:
            return round(self.uniform(low, high), dp)

        ret = [round(self.uniform(low, high), dp) for _ in range(size)]
        if self.ordered:
            return tuple(sorted(ret)[:: -1 if low > high else 1])
        return tuple(ret)


class SelectionRandomiser(ArgumentRandomiser):
    def __init__(self, source, size=None, replacement=False, **kwargs):
        self.source = source
        self.size = size
        self.replacement = replacement
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        source = self.source
        size = self.size

        if size is None:
            return self.choice(source)

        if self.replacement:
            return tuple(self.choices(source, k=size))
        else:
            return tuple(self.sample(source, k=size))
