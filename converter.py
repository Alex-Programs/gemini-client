import urllib

class Node():
    def __init__(self, text, render, _type):
        self.text = text
        self.doRender = render
        self.type = _type

class Text(Node):
    def __init__(self, text):
        super().__init__(text, True, "TEXT")

class Link(Node):
    def __init__(self, text, url, fancyname, baseurl):
        super().__init__(text, True, "LINK")
        self.baseurl = baseurl

        #print("Base URL: " + self.baseurl)
        #print("Original URL: " + url)

        self.url = self.fix_relative(url)

        #print("Changed URL: " + self.url)
        #print("_----------------------------_")

        if fancyname:
            self.fancyname = fancyname

        else:
            self.fancyname = url

    def fix_relative(self, url):
        if not url.startswith("gemini://"):
            if url[0] == "/":
                url = self.baseurl + url
            else:
                url = self.baseurl + "/" + url
        return "?gemini=" + url

class Header(Node):
    def __init__(self, text, raw, level):
        super().__init__(raw, True, "HEADER")
        self.parsedText = text
        self.level = level

class Bullet(Node):
    def __init__(self, text):
        super().__init__(text, True, "BULLET")

class Divider(Node):
    def __init__(self, _type):
        super().__init__("", False, "DIVIDER")
        self.subtype = _type

def convert(text, baseurl):
    nodes = []

    lines = text.split("\n")
    doPre = False
    bullets = False

    whitespaces = [" ", "\t"]

    for line in lines:
        plain = line
        show = True

        if line.startswith("```"):
            if doPre:
                doPre = False
                nodes.append(Divider("PRE_END"))
                line = line[3:]
            else:
                doPre = True
                nodes.append(Divider("PRE_START"))
                line = line[3:]

        if line.startswith("=>") and not doPre:
            url = None
            userFriendly = None

            urlStart = None

            i = 2
            while True:
                i += 1

                if line[i] not in whitespaces:
                    urlStart = i
                    break

            while line[i] not in whitespaces and i < len(line) - 1:
                i += 1

            urlEnd = i

            url = line[urlStart:urlEnd+1]

            userFriendly = line[urlEnd+1:]

            nodes.append(Link(plain, url, userFriendly, baseurl))

        elif line.startswith("#") and not doPre:
            chars = list(line)
            level = 0

            for char in chars:
                if char != "#":
                    break

                level += 1

            nodes.append(Header(line[level:].lstrip(), line, level))

        elif line.startswith("* ") and not doPre:
            if bullets == False:
                bullets = True
                nodes.append(Divider("BULLET_START"))
            nodes.append(Bullet(line[2:]))

        elif show:
            if bullets:
                bullets = False
                nodes.append(Divider("BULLET_END"))

            nodes.append(Text(line))

    return nodes

if __name__ == "__main__":
    import get
    data = get.get("gemini://distro.tube")

    nodes = convert(data.body)

    print(str(nodes))