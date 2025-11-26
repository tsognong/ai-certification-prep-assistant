import requests

my_uri = "https://jsonplacddeholder.typicode.com/todos/1"

try:
    
    response = requests.get(my_uri)


    if (response.status_code) == 200:
        print("Request successful")
        print(response.json())

    else:
        print(f"error: code: {response.status_code}, {response.reason}")

except Exception as e:
    print(f"Exception occurred: {e}")