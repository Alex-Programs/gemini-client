import cgi
import socket
import ssl
import urllib.parse
import ignition

class Success():
    def __init__(self, body, mime):
        self.body = body
        self.mime = mime
        self.type = "SUC"

    def __repr__(self):
        return self.represent()

    def __str__(self):
        return self.represent()

    def represent(self):
        return f"[Mime: {self.mime}, Body: {self.body}]"

class Err():
    def __init__(self, status, mime, message):
        self.status = status
        self.mime = mime
        self.message = message
        self.type = "ERR"

    def __repr__(self):
        return self.represent()

    def __str__(self):
        return self.represent()

    def represent(self):
        return f"[Mime: {self.mime}, Status: {self.status}, Message: {self.message}]"

def add_redirect_data(text, count):
    if count != 0:
        return f"""
INJECTED: Redirect count is {count}

{text}
"""
    
    return text

def get(url):
    redirect_limit = 5

    for redirect_count in range(redirect_limit):
        response = ignition.request(url)

        if response.is_a(ignition.SuccessResponse):
            return Success(add_redirect_data(response.data(), redirect_count), response.meta)

        elif response.is_a(ignition.InputResponse):
            return Err(response.status, response.meta, "Ignition Error: Additional input required. Response: " + add_redirect_data(response.data(), redirect_count))

        elif response.is_a(ignition.RedirectResponse):
            url = response.data().split(" ")[-1]

        elif response.is_a(ignition.TempFailureResponse):
            return Err(response.status, response.meta, "Server Error: Temporary Failure. Response: " + add_redirect_data(response.data(), redirect_count))

        elif response.is_a(ignition.PermFailureResponse):
            return Err(response.status, response.meta, "Server Error: Perm Failure. Response: " + add_redirect_data(response.data(), redirect_count))

        elif response.is_a(ignition.ClientCertRequiredResponse):
            return Err(response.status, response.meta, "Client Certificate Required. Response: " + add_redirect_data(response.data(), redirect_count))

        elif response.is_a(ignition.ErrorResponse):
            return Err(response.status, response.meta, "Error Has Occured: " + add_redirect_data(response.data(), redirect_count))

        else:
            return Err(response.status, response.meta, "Particularly Bad Error - there is no handling for the situation. Data:" + add_redirect_data(response.data(), redirect_count))

    

if __name__ == "__main__":
    print(str(get("gemini://distro.tube")))