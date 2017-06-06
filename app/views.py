from app import app


@app.route('/')
@app.route('/index')
def indexx():
    return '<h1>Hello world!</h1>'