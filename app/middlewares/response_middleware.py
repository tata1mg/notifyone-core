async def add_mandatory_response_headers(request, response):
    # Add `Access-Control-Allow-Origin` header
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
