import urllib

class Node():
    def __init__(self, text, render, _type):
        self.text = text
        self.doRender = render
        self.type = _type

class Text(Node):
    def __init__(self, text, pre):
        super().__init__(text, True, "TEXT")
        self.pre = pre

class Link(Node):
    def __init__(self, text, url, fancyname, baseurl):
        super().__init__(text, True, "LINK")
        self.baseurl = baseurl

        self.url = self.fix_relative(url)
        print(str(self.url))

        if fancyname:
            self.fancyname = fancyname

        else:
            self.fancyname = url

    def fix_relative(self, url):
        absoluted = self.absolutise_url(self.baseurl, url)

        text = "/?gemini=" + absoluted

        result = "/" + text.replace("//", "/")[1:].replace("/", "//", 1)

        return result

    def absolutise_url(self, base, relative):
        if relative[0] != "/":
            relative = "/" + relative
        if "://" not in relative:
            relative = base + relative
        return relative

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
            if not doPre:
                nodes.append(Divider("PRE_START"))

            doPre = (doPre == False)
            show = False

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

            url = line[urlStart:urlEnd]

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

            if doPre:
                nodes.append(Divider("PRE_END"))

            nodes.append(Text(line, doPre))

    return nodes

if __name__ == "__main__":
    import get
    data = get.get("gemini://distro.tube")

    nodes = convert(data.body)

    print(str(nodes))