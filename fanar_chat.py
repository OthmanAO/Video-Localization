import os
from dubbing_utils import FanarAPIClient

def main():
    # Load environment variables
    load_dotenv()
    fanar_api_key = os.getenv("FANAR_API_KEY")
    
    if not fanar_api_key:
        print("Error: FANAR_API_KEY not found in environment variables")
        return
    
    # Initialize API client
    try:
        client = FanarAPIClient(fanar_api_key)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print("Welcome to Fanar Chat!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("-" * 50)
    
    # Initialize conversation history
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit command
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from Fanar
            response = client.fanar_chat(messages)
            assistant_message = response.get("reply", "Sorry, I couldn't generate a response.")
            
            # Add assistant's response to history
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Print response
            print("\nFanar:", assistant_message)
            
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main() 