def is_client_error(error: str):
    last_three = error[-3:]
    code_int = int(last_three)
    return 400 <= code_int <= 499
