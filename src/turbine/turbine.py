import abc
import string


def hello_world():
    return "Hello turbine!"


class Resource:
    def write(records: list, collection_name: string):
        return

    def write(records: list, collection_name: string, **kwargs):
        return

    def records(collection_name: string):
        return

    def records(collection_name: string, **kwargs):
        return


class Turbine(abc):
    def resources():
        return

    def process(records: list, function: function):
        return

    # How to enforce this interface
    @abc.abstractmethod
    def function():
        ...
