from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import GeneratedImage
import os
import json
from pydantic import BaseModel, Field
import google.generativeai as genai
import dashscope
from dashscope import MultiModalConversation

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


def create_image_description_from_dialogue(context, dialogue, target_line, model_name='gemini-1.5-flash'):
    if not settings.GEMINI_API_KEY:
        return {}
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"Error initializing model: {e}")
        return {}

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
        response = model.generate_content(user_prompt)
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        return json.loads(response_text.strip())
    except Exception as e:
        print(f"Error during API call: {e}")
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
        if request.user.profile.token_balance < 1:
            messages.error(request, 'Insufficient tokens. Please purchase more tokens.')
            return redirect('tokens:packages')
        
        context = request.POST.get('context', '')
        dialogue_text = request.POST.get('dialogue', '')
        target_line_index = int(request.POST.get('target_line_index', 0))
        
        character1_image = request.FILES.get('character1')
        character2_image = request.FILES.get('character2')
        background_image = request.FILES.get('background')
        
        dialogue_lines = [line.strip() for line in dialogue_text.split('\n') if line.strip()]
        
        if not dialogue_lines or target_line_index >= len(dialogue_lines):
            messages.error(request, 'Invalid dialogue or target line.')
            return redirect('generator:generate')
        
        target_line = dialogue_lines[target_line_index]
        speaker = target_line.split(":")[0].strip() if ":" in target_line else "Unknown"
        
        speakers = list(set([line.split(":")[0].strip() for line in dialogue_lines if ":" in line]))
        
        image_data = create_image_description_from_dialogue(
            context=context,
            dialogue=dialogue_lines,
            target_line=target_line
        )
        
        if not image_data:
            messages.error(request, 'Failed to generate image description.')
            return redirect('generator:generate')
        
        if not all([character1_image, character2_image, background_image]):
            messages.error(request, 'Please upload all required images (2 characters and background).')
            return redirect('generator:generate')
        
        from django.core.files.storage import default_storage
        char1_path = default_storage.save(f'temp/{character1_image.name}', character1_image)
        char2_path = default_storage.save(f'temp/{character2_image.name}', character2_image)
        bg_path = default_storage.save(f'temp/{background_image.name}', background_image)
        
        char1_full = os.path.join(settings.MEDIA_ROOT, char1_path)
        char2_full = os.path.join(settings.MEDIA_ROOT, char2_path)
        bg_full = os.path.join(settings.MEDIA_ROOT, bg_path)
        
        scene_description = f"""
[Subject]: {image_data.get('subject_description')}
[Setting]: {image_data.get('setting_and_scene')}
[Action]: {image_data.get('action_or_expression')}
[Style]: {image_data.get('camera_and_style')}
[FULL OPTIMIZED IMAGE PROMPT]: {image_data.get('full_image_prompt')}
"""
        
        speaker1 = speakers[0] if len(speakers) > 0 else "Character 1"
        speaker2 = speakers[1] if len(speakers) > 1 else "Character 2"
        
        pr1 = f"You are given three images: Image 1 shows {speaker1}. Image 2 shows {speaker2}. Image 3 shows the background scene. Create a single comic-style scene that combines them:"
        pr2 = f"Add **empty speech bubble** above {speaker} (no text inside). Make the bubble clearly visible and leave enough blank space for dialogue. Ensure characters correspond correctly to their images and fit naturally in the background."
        
        scene_text = pr1 + "\n" + scene_description + "\n" + pr2
        
        if not settings.IMG_API_KEY:
            messages.error(request, 'Image generation API is not configured.')
            return redirect('generator:generate')
        
        conversation_messages = [
            {
                "role": "user",
                "content": [
                    {"image": char1_full},
                    {"image": char2_full},
                    {"image": bg_full},
                    {"text": scene_text}
                ]
            }
        ]
        
        try:
            response = MultiModalConversation.call(
                api_key=settings.IMG_API_KEY,
                model="qwen-image-edit",
                messages=conversation_messages,
                stream=False,
                watermark=False,
                negative_prompt="low quality, distorted face, messy text"
            )
            
            if response.status_code == 200:
                output_image = response.output.choices[0].message.content[0]['image']
                
                request.user.profile.deduct_tokens(1)
                request.user.profile.total_images_generated += 1
                request.user.profile.save()
                
                generated_image = GeneratedImage.objects.create(
                    user=request.user,
                    context=context,
                    dialogue=dialogue_lines,
                    target_line=target_line,
                    speaker=speaker,
                    image_url=output_image,
                    tokens_used=1,
                    subject_description=image_data.get('subject_description', ''),
                    setting_and_scene=image_data.get('setting_and_scene', ''),
                    action_or_expression=image_data.get('action_or_expression', ''),
                    camera_and_style=image_data.get('camera_and_style', ''),
                    full_image_prompt=image_data.get('full_image_prompt', '')
                )
                
                default_storage.delete(char1_path)
                default_storage.delete(char2_path)
                default_storage.delete(bg_path)
                
                messages.success(request, 'Comic scene generated successfully! 1 token used.')
                return render(request, 'generator/result.html', {
                    'image': generated_image,
                    'image_url': output_image
                })
            else:
                messages.error(request, f'Image generation failed: {response.message}')
                return redirect('generator:generate')
                
        except Exception as e:
            messages.error(request, f'Error generating image: {str(e)}')
            return redirect('generator:generate')
    
    return render(request, 'generator/generate.html')


@login_required
def image_gallery(request):
    images = GeneratedImage.objects.filter(user=request.user)
    return render(request, 'generator/gallery.html', {'images': images})
