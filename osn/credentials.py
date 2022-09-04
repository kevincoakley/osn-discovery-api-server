#!/usr/bin/env python

import yaml


def get_credentials(file_name):
    """
    :param: file_name: name of the file containing the credentials
    :return: a dictionary containing the credentials
    """

    with open(file_name) as yaml_file:
        try:
            credentials = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            print(exc)
            return None

        return credentials
