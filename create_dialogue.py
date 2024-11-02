from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime

from config_parser import (
    get_models,
    get_directories,
    format_script_prompt,
    format_screenwriter_prompt,
)


def create_dialogue(
    main_content,
    output_file=None,
    config=None,
):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if config is None:
        raise ValueError("Config must be provided")

    models = get_models(config)
    directories = get_directories(config)
    script_dir = directories["scripts"]

    # Prepare the formatted script prompt
    script_prompts = format_script_prompt(config, main_content)
    messages = [
        {"role": "system", "content": script_prompts["system"]},
        {"role": "user", "content": script_prompts["user"]},
    ]

    # Generate the initial script
    response = client.chat.completions.create(
        model=models["podcast_script"]["model"],
        messages=messages,
        temperature=models["podcast_script"]["temperature"],
        max_tokens=models["podcast_script"]["max_tokens"],
    )

    raw_script = response.choices[0].message.content
    print(f"🤖 raw script created - now enhancing ")

    # Prepare the formatted screenwriter prompt
    screenwriter_prompts = format_screenwriter_prompt(config, raw_script)
    messages = [
        {"role": "system", "content": screenwriter_prompts["system"]},
        {"role": "user", "content": screenwriter_prompts["user"]},
    ]

    # Generate the enhanced script
    response = client.chat.completions.create(
        model=models["podcast_script"]["model"],
        messages=messages,
        temperature=models["podcast_script"]["temperature"],
        max_tokens=models["podcast_script"]["max_tokens"],
    )

    final_script = response.choices[0].message.content
    print(f"🤖 final script created - now saving")

    # Save the script
    if output_file:
        output_path = os.path.join(script_dir, output_file)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(script_dir, f"script_{timestamp}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_script)

    print(f"Script saved to {output_path}")
    return final_script
