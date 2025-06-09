
import requests
import uuid
from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage

class VegasClient:
    _API_ENDPOINT = "http:/"

    def __init__(self, api_key, client_id):
        self.api_key = api_key
        self.client_id = client_id

    def generate_uuid(self):
        return str(uuid.uuid4())

    def make_request(self, use_case, context_id, preSeedInjectionMap, parameters=None):
        transaction_metadata = {
            "clientId": self.client_id,
            "clientTransactionId": self.generate_uuid()
        }

        payload = {
            "inference_type": "generate",
            "user_id": "varan96",
            "agent_id": use_case,
            "task_id": context_id,
            "model": "VEGAS",
            "variables": preSeedInjectionMap
        }

        if parameters:
            payload["parameters"] = parameters

        headers = {
            "Content-Type": "application/json",
            "X-api-key": self.api_key
        }

        response = requests.post(self._API_ENDPOINT, json=payload, headers=headers)
        print("Raw response text:", response.text)  # Print raw response text
        try:
            return response.json()
        except ValueError as e:
            print("Error decoding JSON:", e)
            return None

# Instantiate the client
newclient = VegasClient("nspr-np-6af9bc82-6346-4292-aae8-1d94adb82304", "10221")

# Initialize messages with a greeting from the model
messages = [AIMessage(content="hi how can i help you?", name="Model")]

# Main loop to handle user input
while True:
    question = input("ques: ")
    if question.lower() == "bye":
        for m in messages:
            pprint(m)
        break
    else:
        messages.append(HumanMessage(content=question, name="sravan"))
        
        # PreSeedInjectionMap for testing
        preSeedInjectionMap = {"messages": [message.dict() for message in messages]}
        
        # Make the API request with the current messages
        result = newclient.make_request('dcpaautomation', 'dcpanba', preSeedInjectionMap, {})
        
        # Append the model's response to the messages
        messages.append(AIMessage(content=result, name="Model"))
        
        # Print the result
        print(result)
