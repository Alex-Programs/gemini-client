import cgi
import socket
import ssl
import urllib.parse

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

def absolutise_url(base, relative):
    # Absolutise relative links
    if "://" not in relative:
        # Python's URL tools somehow only work with known schemes?
        base = base.replace("gemini://","http://")
        relative = urllib.parse.urljoin(base, relative)
        relative = relative.replace("http://", "gemini://")
    return relative

def get(url):
    # Do the Gemini transaction
    parsed_url = urllib.parse.urlparse(url)

    try:
        while True:
            s = socket.create_connection((parsed_url.netloc, 1965))
            context = ssl.SSLContext()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            s = context.wrap_socket(s, server_hostname = parsed_url.netloc)
            s.sendall((url + '\r\n').encode("UTF-8"))
            # Get header and check for redirects
            fp = s.makefile("rb")
            header = fp.readline()
            header = header.decode("UTF-8").strip()
            status, mime = header.split()
            # Handle input requests
            if status.startswith("1"):
                # Prompt
                query = input("INPUT" + mime + "> ")
                url += "?" + urllib.parse.quote(query) # Bit lazy...
            # Follow redirects
            elif status.startswith("3"):
                url = absolutise_url(url, mime)
                parsed_url = urllib.parse.urlparse(url)
            # Otherwise, we're done.
            else:
                break
    except Exception as err:
        return Err(None, None, err)

    # Fail if transaction was not successful
    if not status.startswith("2"):
        return Err(status, mime, None)

    # Handle text
    if mime.startswith("text/"):
        # Decode according to declared charset
        mime, mime_opts = cgi.parse_header(mime)
        body = fp.read()
        body = body.decode(mime_opts.get("charset","UTF-8"))
        
        return Success(body, mime)
    # Handle non-text
    else:
        return Success(fp.read(), mime)

if __name__ == "__main__":
    print(str(get("gemini://distro.tube")))