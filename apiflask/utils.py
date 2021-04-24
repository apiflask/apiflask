from werkzeug.http import HTTP_STATUS_CODES


_sentinel = object()


def get_reason_phrase(status_code: int) -> str:
    """A helper function to get the reason phrase of the given status code.

    Arguments:
        status_code: A standard HTTP status code.
    """
    return HTTP_STATUS_CODES.get(status_code, 'Unknown error')
