from app.exceptions.http import HttpException


def get_default_string(value, default):
    """
    get default value
    :param value: value
    :param default: default value
    :return: value
    """
    if value is None or value == '':
        return default
    else:
        return value


def check_int(field, value):
    """
    check integer
    :param field: field name for exception
    :param value: value
    :return: void
    """
    try:
        value = int(value)
    except ValueError:
        raise HttpException(400, field + ' must be an integer')

    if type(value) is not int:
        raise HttpException(400, field + ' must be an integer')

    if int(value) < 0:
        raise HttpException(400, field + ' must be an positive integer')


def check_string(field, value):
    """
    check string
    :param field: field name for exception
    :param value: value
    :return: void
    """
    if type(value) is not str:
        raise HttpException(400, field + ' must be a string')


def check_array(field, value):
    """
    check array
    :param field: field name for exception
    :param value: value
    :return: void
    """
    if not isinstance(value, list):
        raise HttpException(400, field + ' must be an array')


def check_array_item(field, value, item_type):
    """
    check array item type
    :param field: field name for exception
    :param value: array
    :param item_type: item type
    :return: void
    """
    # check is array
    check_array(field, value)

    # check array item type
    for item in value:
        if item_type == 'int':
            check_int(field, item)
        elif item_type == 'string':
            check_string(field, item)


def check_choices(field, value, choices):
    """
    check value is in choices
    :param field: field name for exception
    :param value: value
    :param choices: available value list
    :return: void
    """
    if value not in choices:
        raise HttpException(400, field + ' should be one of these: ' + ', '.join(choices))
