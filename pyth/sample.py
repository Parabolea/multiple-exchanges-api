import websockets
import asyncio
import json

sample_data = {
    "name": "Alice",
    "age": 30,
    "is_student": False,
    "courses": ["Math", "Physics"],
    "address": {
        "city": "Wonderland",
        "zipcode": "12345"
    }
}

class Test:
    def __init__(self, model, year):
        self.model = model
        self.year = year
    def output(self):
        print(f"The model is {self.model} and the year is {self.year}")
        return 'geriogjer'

async def handler(websocket, path):
    data = 'test' # Replace with your logic
    await websocket.send(data)

print(__name__)
if __name__ == "__main__":
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print('ws connection is running')
    asyncio.get_event_loop().run_forever()

# test = Test("Mazda", "2023")
    # print(test.output())
    # print(sample_data)
    # print(json.dumps(sample_data))