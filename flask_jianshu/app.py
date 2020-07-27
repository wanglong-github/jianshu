from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    x=[{
        'name':'牛肉','value':500},
        {'name':'牛肉','value':500},
        {'name':'牛肉','value':500},
    ]
    return render_template('index.html',)


if __name__ == '__main__':
    app.run()
