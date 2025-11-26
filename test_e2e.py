import requests
BASE_URL = "http://127.0.0.1:8000"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")

def test_chat():
    print_separator("Starting End-to-End Session Test")
    
    session_id = None
    
    # Turn 1: Research Flow
    print("\n[Turn 1] User: 'What is the RTI fee in Karnataka?'")
    payload = {"message": "What is the RTI fee in Karnataka?"}
    if session_id:
        payload["session_id"] = session_id
        
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        session_id = data["session_id"]
        
        print(f"Status: {response.status_code}")
        print(f"Session ID: {session_id}")
        print(f"Intent: {data['analysis']['intent']}")
        print(f"Reply: {data['reply'][:100]}...")
        
        if data['analysis']['intent'] != "info":
            print("❌ FAILED: Expected intent 'info'")
        else:
            print("✅ PASSED: Research Flow")
            
    except Exception as e:
        print(f"❌ FAILED: Connection error. Is the server running? {e}")
        return

    # Turn 2: Clarification Flow (Ambiguous Request)
    print_separator("Testing Context & Clarification")
    print("\n[Turn 2] User: 'I want to draft an application for my missing internal marks.'")
    payload = {"message": "I want to draft an application for my missing internal marks.", "session_id": session_id}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Intent: {data['analysis']['intent']}")
        print(f"Reply: {data['reply']}")
        
        if data['analysis']['intent'] != "clarify":
            print("❌ FAILED: Expected intent 'clarify' (missing details)")
        else:
            print("✅ PASSED: Clarification Flow")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")

    # Turn 3: Legal Advisory Flow (Problem Statement)
    print_separator("Testing Legal Advisory Flow")
    print("\n[Turn 3] User: 'The Police Station refused to take my FIR. What should I do?'")
    payload = {"message": "The Police Station refused to take my FIR. What should I do?", "session_id": session_id}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Intent: {data['analysis']['intent']}")
        print(f"Reply: {data['reply'][:300]}...")
        
        if data['analysis']['intent'] != "legal_advice":
            print("❌ FAILED: Expected intent 'legal_advice'")
        else:
            print("✅ PASSED: Legal Advisory Flow")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_chat()
