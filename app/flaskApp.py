#flaskApp.py

from bokeh.client import pull_session
from bokeh.embed import server_document
from flask import Flask, render_template
from flask import send_from_directory

app = Flask(__name__)


# locally creates a page
@app.route('/')
def index():
            # generate a script to load the customized session
    script = server_document(url=link)
            # use the script in the rendered page
    return render_template("embed.html", script=script, template="Flask")


if __name__ == '__main__':
    # runs app in debug mode
    app.run(port=5001, host='0.0.0.0', debug=False)
    # app.run()