from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import GeneratedImage
import os
import json
from pydantic import BaseModel, Field
import dashscope
from dashscope import MultiModalConversation
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .tasks import generate_image_for_line
from django.contrib.auth.models import User
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMG_API_KEY = os.getenv('IMG_API_KEY')

# Read key

dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL




class ImagePrompt(BaseModel):
    subject_description: str = Field(
        ...,
        description="Detailed description of the character speaking the line, including mood, attire, and physical posture."
    )
    setting_and_scene: str = Field(
        ...,
        description="The environment, lighting, time of day, and general atmosphere surrounding the character and the dialogue."
    )
    action_or_expression: str = Field(
        ...,
        description="The specific action, facial expression, or emotional intensity captured in the moment the line is delivered."
    )
    camera_and_style: str = Field(
        ...,
        description="Recommended artistic style (e.g., cinematic, watercolor), camera angle (e.g., close-up, wide shot), and general visual mood."
    )
    full_image_prompt: str = Field(
        ...,
        description="A single, cohesive, highly detailed prompt combining all elements, optimized for image generation."
    )


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


@login_required
def dashboard_view(request):
    recent_images = GeneratedImage.objects.filter(user=request.user)[:10]
    return render(request, 'generator/dashboard.html', {
        'recent_images': recent_images,
        'user': request.user
    })


@login_required
def generate_view(request):
    if request.method == 'POST':
        # --- Check token balance ---
        if request.user.profile.token_balance < 1:
            messages.error(request, 'Insufficient tokens. Please purchase more tokens.')
            return redirect('tokens:packages')

        # --- Read text fields ---
        context = request.POST.get('context', '')
        dialogue_text = request.POST.get('dialogue', '')
        target_line_index = int(request.POST.get('target_line_index', 0))

        # --- Split dialogue into lines ---
        dialogue_lines = [line.strip() for line in dialogue_text.split('\n') if line.strip()]
        if not dialogue_lines:
            messages.error(request, 'Invalid dialogue or empty input.')
            return redirect('generator:generate')

        # --- Dynamically collect characters ---
        characters = []
        i = 1
        while True:
            name_key = f'character_name_{i}'
            img_key = f'character_image_{i}'
            name = request.POST.get(name_key)
            img = request.FILES.get(img_key)
            if not name or not img:
                break
            characters.append({'name': name, 'image': img})
            i += 1

        if len(characters) < 1:
            messages.error(request, 'Please upload at least one character.')
            return redirect('generator:generate')

        # --- Background info ---
        background_name = request.POST.get('background_name', 'background')
        background_image = request.FILES.get('background')

        if not background_image:
            messages.error(request, 'Please upload a background image.')
            return redirect('generator:generate')

        # --- Save all uploaded files temporarily ---
        from django.core.files.storage import default_storage
        saved_files = []
        try:
            for char in characters:
                path = default_storage.save(f"temp/{char['image'].name}", char["image"])
                char["path"] = os.path.join(settings.MEDIA_ROOT, path)
                saved_files.append(path)

            bg_path = default_storage.save(f'temp/{background_image.name}', background_image)
            background_full = os.path.join(settings.MEDIA_ROOT, bg_path)
            saved_files.append(bg_path)

            # --- Loop through all dialogue lines ---
            all_results = []
            for i, line in enumerate(dialogue_lines):
                generate_image_for_line.delay(
                    user_id=request.user.id,
                    context=context,
                    dialogue=dialogue_lines,
                    target_line=line,
                    characters=characters,
                    background_image_path=background_full,
                )
    
            messages.success(request, "Your request is being processed. Check back later in your gallery.")
            return redirect('generator:image_gallery') 
        except Exception as e:
            # handle the error, clean up or show message
            messages.error(request, f"An error occurred: {e}")
            # optionally clean up saved files here or re-raise
            for path in saved_files:
                default_storage.delete(path)
            return redirect('generator:generate')
    return render(request, 'generator/generate.html')
@login_required
def image_gallery(request):
    images = GeneratedImage.objects.filter(user=request.user)
    return render(request, 'generator/gallery.html', {'images': images})
