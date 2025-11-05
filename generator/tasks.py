# generator/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from .models import GeneratedImage
import os
from .views import MultiModalConversation
from .image_utils import create_image_description_from_dialogue
from django.conf import settings

@shared_task
def generate_image_for_line(
    user_id,
    context,
    dialogue,
    target_line,
    characters,
    background_image_path,
):
    User = get_user_model()
    user = User.objects.get(id=user_id)

    image_data = create_image_description_from_dialogue(
        context=context,
        dialogue=dialogue,
        target_line=target_line,
    )
    if not image_data:
        return "Failed to get image description"

    speaker = target_line.split(":")[0].strip() if ":" in target_line else "Unknown"

    char_text = ", ".join([c['name'] for c in characters])
    images_desc = ", ".join([f'{c["name"]}' for c in characters])
    pr1 = f"You are given several images: {images_desc}, and one background image showing scene."
    pr2 = f"Create a comic-style scene showing the moment when {speaker} says his line."
    pr3 = f"Add an empty speech bubble above {speaker} (no text)."
    pr4 = "Ensure characters appear natural in the scene and maintain their visual style."
    scene_text = pr1 + "\n" + json.dumps(image_data, indent=2) + "\n" + pr2 + "\n" + pr3 + "\n" + pr4

    message_content = []
    for char in characters:
        message_content.append({"image": char["path"]})
    message_content.append({"image": background_image_path})
    message_content.append({"text": scene_text})

    try:
        response = MultiModalConversation.call(
            api_key=settings.IMG_API_KEY,
            model="qwen-image-edit",
            messages=[{"role": "user", "content": message_content}],
            stream=False,
            watermark=False,
            negative_prompt="low quality, distorted face, messy text"
        )
        if response.status_code == 200:
            output_image = response.output.choices[0].message.content[0]['image']

            GeneratedImage.objects.create(
                user=user,
                context=context,
                dialogue=dialogue,
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

            user.profile.deduct_tokens(1)
            user.profile.total_images_generated += 1
            user.profile.save()
            return "Success"
        else:
            return f"API failed with status {response.status_code}"
    except Exception as e:
        return str(e)
