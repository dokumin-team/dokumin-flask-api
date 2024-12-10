from app import create_app

app = create_app()

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(port=8000, debug=True)
    # add host='0.0.0.0' when push to docker
