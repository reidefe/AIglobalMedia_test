from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from typing import Callable

def create_images_with_text(
    data: pd.DataFrame,
    sample_image_path: str,
    output_dir: str,
    row_limit: int = 0,
    log_callback: Callable[[str], None] = print
) -> None:
    """
    Generates two images for each record in the cleaned data using specified columns
    and saves them in a folder named after another column or a fallback.

    Parameters:
    ----------
    data : pd.DataFrame
        The cleaned pandas DataFrame.

    sample_image_path : str
        The path to the sample image to use as a template.

    output_dir : str
        The directory to save the generated images.

    row_limit : int, optional
        The number of rows to process. If 0, all rows are processed (default: 0).

    log_callback : Callable[[str], None], optional
        A callback function to log messages (default: print).

    Returns:
    -------
    None
    """
    def log(message: str):
        """Logs messages to the log_callback."""
        log_callback(message)

    # Load the sample image
    try:
        sample_image = Image.open(sample_image_path)
    except Exception as e:
        log(f"Error loading sample image: {e}")
        return

    if sample_image.mode != "RGB":
        sample_image = sample_image.convert("RGB")

    # Skip the first row and limit rows if specified
    data_to_process = data.iloc[1:].head(row_limit) if row_limit > 0 else data.iloc[1:]
    log(f"Processing {len(data_to_process)} records for image generation (excluding the first row).")

    for i, row in data_to_process.iterrows():
        # Extract folder name and text fields
        folder_name = str(row.get("Column_3", "")).strip()
        text_1 = str(row.get("Column_6", "")).strip()
        text_2 = str(row.get("Column_9", "")).strip()
        shared_text_1 = str(row.get("Column_8", "")).strip()
        shared_text_2 = str(row.get("Column_5", "")).strip()

        # Ignore "MISSING" values
        text_1 = "" if text_1 == "MISSING" else text_1
        text_2 = "" if text_2 == "MISSING" else text_2
        shared_text_1 = "" if shared_text_1 == "MISSING" else shared_text_1
        shared_text_2 = "" if shared_text_2 == "MISSING" else shared_text_2

        # If folder_name is missing, use fallback columns to create a unique folder name
        if not folder_name:
            fallback_name = "_".join(
                str(row.get(col, "")).strip() for col in ["Column_8", "Column_4"] if str(row.get(col, "")).strip()
            )
            folder_name = fallback_name if fallback_name else None

        # Skip rows if no valid folder name can be generated
        if not folder_name:
            log(f"Skipping Record {i + 1}: No valid folder name available.")
            continue

        log(f"Record {i + 1}: Creating folder '{folder_name}' and generating images.")

        # Create the folder for the domain
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Helper function to dynamically adjust font size
        def get_fit_font(draw, text, image_size, initial_font_size):
            font_size = initial_font_size
            font = ImageFont.truetype("arial.ttf", size=font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            while text_width > image_size[0] - 20 or text_height > image_size[1] - 20:  # Leave a margin of 20px
                font_size -= 2
                if font_size < 10:  # Minimum font size to prevent infinite loop
                    break
                font = ImageFont.truetype("arial.ttf", size=font_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            return font

        def draw_text_with_hierarchy(draw, img, texts, initial_font_sizes):
            """Draws texts hierarchically on the image."""
            y_offset = (img.size[1] - sum(initial_font_sizes)) // 2  # Center vertically
            for idx, (text, font_size) in enumerate(zip(texts, initial_font_sizes)):
                if not text:  # Skip blank texts
                    continue
                font = get_fit_font(draw, text, img.size, font_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x = (img.size[0] - text_width) // 2  # Center horizontally
                draw.text((x, y_offset), text, font=font, fill="darkblue", align="center")
                y_offset += text_height + 20  # Space between text lines

        # Generate the first image (shared_text_1, shared_text_2, and text_1)
        img = sample_image.copy()
        draw = ImageDraw.Draw(img)
        draw_text_with_hierarchy(
            draw, img, texts=[shared_text_1, shared_text_2, text_1], initial_font_sizes=[60, 40, 20]
        )
        img.save(os.path.join(folder_path, f"image_1_{i}.png"))
        log(f"Saved image 1 for Record {i + 1} in {folder_path}.")

        # Generate the second image (shared_text_1, shared_text_2, and text_2)
        img = sample_image.copy()
        draw = ImageDraw.Draw(img)
        draw_text_with_hierarchy(
            draw, img, texts=[shared_text_1, shared_text_2, text_2], initial_font_sizes=[60, 40, 20]
        )
        img.save(os.path.join(folder_path, f"image_2_{i}.png"))
        log(f"Saved image 2 for Record {i + 1} in {folder_path}.")

    log("Image generation complete.")
