from typing import Tuple, Any


class Validator:
    """Validation class."""
    @staticmethod
    def validate(request: dict) -> Tuple[Any, str]:
        """Ensure that the request is valid."""
        if not request:
            # if request is empty, return an error message
            return None, "request is empty."
        error_message = None
        expected_keys = ["Amount", "pnr"]
        for key in expected_keys:
            if request.get(key) is None:
                error_message = f"missing key ~ <{key}>."
                break
            if not request.get(key):
                error_message = f"<{key}> cannot be empty."
                break
            try:
                if key == 'Amount' and int(request.get('Amount')) <= 0:
                    error_message = f"<{key}> cannot be less than or equal to zero."
            except ValueError as _:
                error_message = f"<{key}> must be a number."
        if not error_message:
            # convert the amount to an integer, and rename the `Amount` key to `amount`
            # before returning the request
            amount = int(request.get('Amount'))
            del request['Amount']
            request['amount'] = amount
        return request, error_message
