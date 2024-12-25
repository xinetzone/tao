from functools import update_wrapper
from bytecode import Bytecode, Instr
import logging
# logging.basicConfig(level=logging.INFO)


class LoggedAccess:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.private_name)
        logging.debug('Accessing %r giving %r', self.public_name, value)
        return value

    def __set__(self, obj, value):
        logging.debug('Updating %r to %r', self.public_name, value)
        setattr(obj, self.private_name, value)


class trace:
    cache = {}
    is_activate = False
    variable = LoggedAccess()
    def __init__(self, variable="result"):
        self.variable = variable

    def __call__(self, func):
        if not type(self).is_activate:
            return func
        func = self.transform(func)
        def wrapper(*args, **kwargs):
            res, values = func(*args, **kwargs)
            type(self).cache[func.__qualname__].append((self.variable, values))
            return res
        return update_wrapper(wrapper, func)

    def transform(self, func):
        type(self).cache[func.__qualname__] = []
        c = Bytecode.from_code(func.__code__)
        extra_code = [
            Instr('STORE_FAST', '_res'),
            Instr('LOAD_FAST', self.variable),
            Instr('STORE_FAST', '_value'),
            Instr('LOAD_FAST', '_res'),
            Instr('LOAD_FAST', '_value'),
            Instr('BUILD_TUPLE', 2),
            Instr('STORE_FAST', '_result_tuple'),
            Instr('LOAD_FAST', '_result_tuple'),
         ]
        c[-1:-1] = extra_code
        func.__code__ = c.to_code()
        return func

    @classmethod
    def clear(cls):
        cls.cache.clear()

    @classmethod
    def activate(cls):
        cls.is_activate = True
