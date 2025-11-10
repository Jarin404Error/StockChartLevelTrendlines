import os
from dotenv import load_dotenv
from google import genai


def get_gemini_analysis(levels, current_price, ticker):
    """
    Sends the current market data to the Gemini API for a dynamic analysis.
    
    Args:
        levels: Dictionary of level names and prices
        current_price: Current stock price
        ticker: Stock ticker symbol
        
    Returns:
        str: AI-generated analysis or error message
    """
    print("Getting dynamic Gemini AI analysis...")
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # This debug message was super helpful
            print("--- DEBUG: FAILED TO LOAD GEMINI_API_KEY! ---")
            print("--- Make sure .env file has GEMINI_API_KEY=... ---")
            return "**Could not retrieve Gemini analysis.** Is your GEMINI_API_KEY set in the .env file?"
        
        print("--- DEBUG: Gemini API Key loaded successfully. ---")
        
        # Initialize Gemini client with API key
        client = genai.Client(api_key=api_key)
        
        # Format the data into a clean string for the AI
        level_summary = "\n".join([f"  {name}: {price:.2f}" for name, price in levels.items() if price])
        
        # Create the user prompt
        # The prompt engineering part is tricky. Trying to make it neutral.
        # Explicitly telling it NOT to give advice.
        prompt = f"""
        You are a neutral, educational trading assistant. 
        You NEVER give financial advice, predictions, or recommendations (e.g., "buy calls", "sell puts", "the price will go up").
        Your role is to analyze the provided market data and give a brief, educational summary
        of the current situation. Focus on the price's relationship to the key levels.
        Keep your response to 3-4 short bullet points or a short paragraph.

        Here is the current market data for {ticker}:

        Current Price: {current_price:.2f}

        Key Levels:
        {level_summary}

        Please provide a brief, educational analysis of the current situation. 
        What might a trader be observing? 
        (REMEMBER: Do not give any advice or predictions).
        """
        
        # Make the API Call
        print("--- DEBUG: Sending prompt to Gemini... ---")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        
        # Return the AI's text response
        return response.text
        
    except Exception as e:
        print(f"Error getting Gemini analysis: {e}")
        return f"**Could not retrieve Gemini analysis.** An error occurred: {e}"


# Simple test code (only runs when executed directly)
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("GEMINI_API_KEY not found in .env file")
    else:
        # Initialize Gemini client with API key
        client = genai.Client(api_key=api_key)
        
        # Fetch content from Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Explain how AI works in a few words",
        )
        
        print(response.text)
