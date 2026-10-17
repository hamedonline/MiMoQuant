from typing import Callable
from utils.entities.data_types import ExecutionFunction


class ExecutionQueue:
    def __init__(self, *functions):
        self.execution_list = []
        self.add_functions(*functions)

    def add_functions(self, *functions: ExecutionFunction):
        """
        Adds multiple functions to the execution list.
        """
        for func_tuple in functions:
            if len(func_tuple) == 4: # priority is provided
                func, args, kwargs, priority = func_tuple
                if self._check_input_validity(func, args, kwargs):
                    self._register_function(func, args, kwargs, priority)
            elif len(func_tuple) == 3: # no priority value provided
                func, args, kwargs = func_tuple # type: ignore
                if self._check_input_validity(func, args, kwargs):
                    self._register_function(func, args, kwargs, float('inf'))
            else:
                raise ValueError("Each function entry must be a tuple of length 3 or 4.")

        self._sort_execution_list()
        self._reset_priorities()

    def _check_input_validity(self, func: Callable, args: tuple, kwargs: dict) -> bool:
        """
        Checks the validity of a single queue input.
        """
        if not callable(func):
            raise ValueError(f"Function {func} is not callable.")
        if not isinstance(args, tuple):
            raise ValueError(f"Arguments {args} must be provided in tuple format.")
        if not isinstance(kwargs, dict) and not callable(kwargs):
            raise ValueError(f"Keyword arguments {kwargs} must be provided in dictionary format or as a callable.")
        return True


    def _register_function(self, func, args, kwargs, priority):
        function_info = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'priority': priority
        }
        self.execution_list.append(function_info)


    def _sort_execution_list(self):
        """
        Sorts the execution list based on the priority of the functions.
        """
        self.execution_list.sort(key=lambda x: x['priority'])


    def _reset_priorities(self):
        """
        Resets the priorities of the functions in the execution list.
        For example, execution queue with priorities [0, 1, 2, 4, 9] will get the priority numbers reset to [0, 1, 2, 3, 4].
        """
        for idx, item in enumerate(self.execution_list):
            if item['priority'] != idx:
                self.execution_list[idx] = {
                    'func': item['func'],
                    'args': item['args'],
                    'kwargs': item['kwargs'],
                    'priority': idx
                }


    def print_execution_list(self):
        """
        Prints the execution list in the order they will be executed.
        """
        for idx, item in enumerate(self.execution_list):
            print(f"{idx + 1}. {item['func'].__name__}(*{item['args']}, **{item['kwargs']}) with priority {item['priority']}")


    def execute_all(self):
        for function_info in self.execution_list:
            kwargs = function_info['kwargs']
            if callable(kwargs):
                kwargs = kwargs()
            # ensure kwargs is a dictionary
            if not isinstance(kwargs, dict):
                kwargs = {}
            function_info['func'](
                *function_info['args'],
                **kwargs
            )


    def clear(self):
        self.execution_list = []
