from flask import Flask,jsonify,request
from flask import render_template
import ast


app = Flask(__name__)

hashtags = []
counts = []


@app.route("/")
def get_chart():
    global hashtags,counts
    hashtags = []
    counts = []
    return render_template('index.html', counts_data=counts, hashtags_data=hashtags)


@app.route('/refreshDashboard')
def refresh_graph_data():
    global hashtags, counts
    return jsonify(r_hashtags=hashtags, r_counts=counts)


@app.route('/updateDashboard', methods=['POST'])
def update_data_post():
    global hashtags, counts
    if not request.form or 'data' not in request.form:
        return "error: no data",400
    hashtags = ast.literal_eval(request.form['label'])
    counts = ast.literal_eval(request.form['data'])
    return "success",201


if __name__ == "__main__":
    app.run(host='localhost', port=5003)

