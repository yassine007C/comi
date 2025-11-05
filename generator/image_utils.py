import dashscope
from dashscope import MultiModalConversation
from google import genai
from google.genai import types

def create_image_description_from_dialogue(
    context: str,
    dialogue: list[str],
    target_line: str,
    model_name: str = 'gemini-2.5-flash' # Use a powerful model for complex reasoning
) -> dict:
    """
    Generates a structured image description based on a specific line of dialogue, 
    using the surrounding context and full conversation.
    """

    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing client. Ensure GEMINI_API_KEY is set. Details: {e}")


    system_instruction = (
        "You are an expert visual storyteller and image prompt generator. Your task is to take a piece of dialogue "
        "and its context, and produce a highly detailed, cinematic description suitable for a text-to-image AI. "
        "Focus on the moment the target line is delivered. The main focus should be the speaking character, but "
        "include other relevant characters if their presence enhances the visual storytelling. Depict the atmosphere, "
        "lighting, and emotional tone naturally. Occasionally (about 40% of the time), widen the scene to include "
        "both the speaker and other characters. Return a JSON object with these fields: subject_description, "
        "setting_and_scene, action_or_expression, camera_and_style, full_image_prompt."
    )
    
    user_prompt = f"""{system_instruction}

    CONTEXT: {context}

    FULL DIALOGUE:
    {chr(10).join(dialogue)}

    TARGET LINE TO VISUALIZE:
    "{target_line}"

    Analyze the target line and the full situation. Describe the moment the line is delivered, 
    including the speaker and any other characters visible or reacting in the same frame. 
    Capture emotional tension, lighting, and the spatial relationship between characters.
    Generate the structured JSON response.
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ImagePrompt,
            ),
        )
        print(json.loads(response.text))
        # The response.text is a strict JSON string due to response_mime_type
        return json.loads(response.text)

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return {}

