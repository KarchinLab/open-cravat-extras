"""
API helper functions
"""


def oc_response(code, message, **kwargs):
    """
    Quick helper function for JSON responses, will take the HTTP code, a message and data to return and formats
    it in a way that flask likes
    :param code: the HTTP status code
    :param message: a message about the response
    :param kwargs: the data to return
    :return: a formatted tuple, JSON response first, then the HTTP status code
    """
    return {'code': code, 'body': message, **kwargs}, code


