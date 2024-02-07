#!/usr/bin/env python

import yaml


def get_bucket_ignore_list(file_name):
    """
    :param: file_name: name of the file containing the list of buckets to ignore
    :return: a dictionary containing the buckets to ignore
    """

    try:
        with open(file_name) as yaml_file:
            try:
                bucket_ignore_list = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                print(exc)
                return {}
    except FileNotFoundError as exc:
        print(exc)
        return {}

    return bucket_ignore_list
