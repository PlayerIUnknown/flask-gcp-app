from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello, Google Cloud! Your application is live!</h1>'

if __name__ == '__main__':
    # Run the app on all available network interfaces (0.0.0.0) on port 80
    app.run(host='0.0.0.0', port=8080)
