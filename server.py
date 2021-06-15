from flask import Flask, send_from_directory, render_template_string
from flask.templating import render_template
from flask import request
import get
import converter

app = Flask(__name__)

@app.route("/index.html")
@app.route("/index")
@app.route("/")
def index():
    uri = request.args.get("gemini")

    #TODO Error handling

    resp = get.get(uri)

    if resp.type == "ERR":
        return f"Error: {resp.status}, {resp.mime}, {resp.message}"

    print(str(resp.body))

    nodes = converter.convert(resp.body, uri)

    return render_template("index.html", nodes=nodes, Node=converter.Node, Text=converter.Text, Link=converter.Link, Header=converter.Header, Bullet=converter.Bullet)

@app.route("/assets/<path:path>")
def send_assets(path):
    return send_from_directory("assets/", path)

app.run(host="0.0.0.0", port=8010, debug=True)