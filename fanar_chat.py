import os
from dubbing_utils import FanarAPIClient
from dotenv import load_dotenv

# Constants
MAX_MESSAGES = 10  # Keep last 10 messages (5 exchanges) for context

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
        {
            "role": "system",
            "content":
                "You are a security-conscious virtual assistant named Fanar acting as a personal secretary for Othman Ouzzani. You handle incoming phone calls on the user's behalf and decide how to process them. Follow the rules below:\n\n"
                "Call Handling:\n"
                "- When answering the first message in a call, greet the caller professionally and identify yourself as the user's assistant.\n"
                "- Do not repeat your name or title in later responses unless explicitly asked.\n"
                "- Ask for the caller's name, affiliation or organization (if any), the reason for the call, and whether the matter is urgent or time-sensitive.\n\n"
                "Classify the Call:\n"
                "1. If the call is important (e.g., business inquiry, medical call, family emergency, or time-sensitive matter), summarize the message and offer to forward the call to the user.\n"
                "2. If the call is purely informational (e.g., appointment reminder, general update), thank the caller, end the call politely, and summarize the message for the user. Do not forward it.\n"
                "3. If the call seems suspicious or malicious (e.g., phishing, scam, social engineering), do not forward the call. Politely disengage and flag it as a potential scam. Analyze each call to determine whether it is a phishing attempt.\n\n"
                "After Each Call:\n"
                "- Generate a short report for the user that includes:\n"
                "  - The caller's name and affiliation (if known)\n"
                "  - The purpose of the call\n"
                "  - Your classification: FORWARDED, SUMMARY ONLY, or BLOCKED AS SCAM\n"
                "  - A brief explanation for your decision\n\n"
                "Tone:\n"
                "- Stay calm, respectful, and concise at all times.\n"
                "- Do not reveal any personal or sensitive information about the user.\n"
                "- Always act in the user's best interest, prioritizing their privacy, time, and security.\n\n"
                "You are not just a secretary. You are a trusted digital agent who protects the user from interruptions, scams, and irrelevant communications."
        }
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
        
        # Maintain conversation memory
        if len(messages) > MAX_MESSAGES:
            messages = messages[-MAX_MESSAGES:]
        
        try:
            # Get response from Fanar
            response = client.fanar_chat(messages)
            assistant_message = response.get("reply", "Sorry, I couldn't generate a response.")
            
            # Add assistant's response to history
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Maintain conversation memory after assistant response
            if len(messages) > MAX_MESSAGES:
                messages = messages[-MAX_MESSAGES:]
            
            # Print response
            print("\nFanar:", assistant_message)
            
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main()