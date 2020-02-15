from aiohttp import web

default_errors = {
    400: {
        "error": "Bad Request",
        "message": "The request you submitted did not meet the requirements"
        + " defined by the API. Please check your request and try again.",
    },
    404: {
        "error": "Not Found",
        "message": "We were unable to find the resource you requested."
        + " Please check your request and try again.",
    },
    500: {
        "error": "Server Error",
        "message": "We were unable to process your request."
        + " Please check that you submitted it correctly and then try again.",
    },
}


async def api_error(code=500, error=None, message=None, formatter=web.json_response):
    """
    Generates an API error response object which allows you to customize
    the error name and message for any given error.
    """

    default_error = default_errors.get(
        code,
        {
            "error": "Server Error",
            "message": "We were unable to process your request."
            + " Please check that you submitted it correctly and then try again.",
        },
    )

    return formatter(
        {
            "code": code,
            "error": error or default_error["error"],
            "message": message or default_error["message"],
        },
        status=code,
    )
