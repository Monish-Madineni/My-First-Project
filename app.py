from flask import Flask, render_template
app=Flask(__name__)

type=['GOVT','PVT','UNIV']

@app.route("/")
def hello():
    return render_template('browse1.html',TYPE=type)
if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)