import os
import random
import time

import requests
from PIL import Image
from io import BytesIO

from agent.config import IMAGE_MODEL ,IMAGE_SIZE ,IMAGE_QUALITY
from agent.state import ContentGenerationState


def generate_image(state: ContentGenerationState):
    """Generate an image for the content using DALL·E."""
    # Import OpenAI client here to avoid circular imports
    from main import client

    image_prompt = state["image_prompt"]

    try:
        # Using OpenAI's DALL·E model for image generation
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=image_prompt,
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
            n=1,
        )

        image_url = response.data[0].url

        # Download and save the image locally
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))

        # Create images directory if it doesn't exist
        if not os.path.exists("../images"):
            os.makedirs("../images")

        # Save the image
        filename = f"images/blog_image_{time.time()}.png"
        img.save(filename)

        return {"image_url": filename}

    except Exception as e:
        print(f"Error generating image: {e}")
        return {"image_url": "https://via.placeholder.com/800x400?text=AI+Blog+Image"}