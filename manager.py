from quart import Quart


app = Quart(__name__)


@app.route('/receive', methods=['POST'])
async def receive():
    ...


if __name__ == '__main__':
    app.run()
