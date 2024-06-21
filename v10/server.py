from flask import Flask, request 

app = Flask(__name__)

@app.route('/switch')
def hello():
    number = request.args.get('number')
    delay = request.args.get('delay') 
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()