import json
import os
import time


def get_cache(file_name):
    """
    :param: file_name: name of the file containing the cache
    :return: the cached values in the file
    """

    if os.path.exists(file_name):
        modification_time = os.path.getmtime(file_name)
        current_time = time.time()
        time_difference = current_time - modification_time

        if time_difference < (86100):  # 23:55 hours:mintues in seconds
            with open(file_name, "r") as read_file:
                try:
                    cache = json.load(read_file)
                    return cache
                except json.JSONDecodeError as exc:
                    print(exc)
                    return {}
        else:
            return {}
    else:
        return {}


def write_cache(file_name, cache):
    """
    :param: file_name: name of the file to write the cache
    :param: cache: the cache to write to the file
    """

    with open(file_name, "w") as write_file:
        json.dump(cache, write_file)
