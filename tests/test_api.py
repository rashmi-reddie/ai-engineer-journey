import requests

BASE_URL="http://127.0.0.1:8000"

def test_health():
    response=requests.get(f"{BASE_URL}/")
    print("Health check:",response.json())
    
def test_chat(session_id,message):
    payload={
        "session_id":session_id,
        "message":message,
        "system_prompt":"You are a helpful mentor. Be brief and precise"
    }
    response=requests.post(f"{BASE_URL}/chat",json=payload)
    data=response.json()
    print(f"Turn {data['turn_count']} : {data['reply'][:100]}...")
    return data

def test_memory():
    print("\n--- Testing memory ---")
    test_chat("test_session","My name is Rashmitha and I love Python")
    test_chat("test_session","Iam from Hyderabad")
    result=test_chat("test_session","What is my name? and where am i from?")
    print("\nFull reply:",result["reply"])

if __name__=="__main__":
    test_health()
    test_memory()