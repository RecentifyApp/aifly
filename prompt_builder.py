def build_prompt(base_prompt, location, camera):

    location_prompt = {
        "Beach": "tropical beach background",
        "Gym": "modern gym environment",
        "Coffee shop": "aesthetic coffee shop",
        "Luxury hotel": "luxury hotel lobby",
        "Street": "urban street fashion scene"
    }

    camera_prompt = {
        "iPhone": "iphone selfie photo",
        "DSLR": "professional dslr photography",
        "Mirror": "mirror selfie photo",
        "Studio": "professional studio lighting"
    }

    prompt = f"""
    {base_prompt},
    instagram influencer,
    ultra realistic,
    high detail skin texture,
    {location_prompt.get(location,'')},
    {camera_prompt.get(camera,'')}
    """

    return prompt
