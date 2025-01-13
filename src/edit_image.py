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

    # Set the base font size
    base_font_size = 40

    # Skip the first row and limit rows if specified
    data_to_process = data.iloc[1:].head(row_limit) if row_limit > 0 else data.iloc[1:]
    log(f"Processing {len(data_to_process)} records for image generation (excluding the first row).")

    for i, row in data_to_process.iterrows():
        # Extract folder name and image texts
        folder_name = str(row.get("Column_3", "")).strip()
        text_1 = str(row.get("Column_6", "")).strip()
        text_2 = str(row.get("Column_9", "")).strip()

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

        # Generate the first image if text_1 is not empty
        if text_1:
            img = sample_image.copy()
            draw = ImageDraw.Draw(img)
            font = get_fit_font(draw, text_1, img.size, base_font_size)
            bbox = draw.textbbox((0, 0), text_1, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (img.size[0] - text_width) // 2
            y = (img.size[1] - text_height) // 2
            draw.text((x, y), text_1, font=font, fill="black", align="center")
            img.save(os.path.join(folder_path, f"image_column_3_{i}.png"))
            log(f"Saved image from 'column_3' for Record {i + 1} in {folder_path}.")

        # Generate the second image if text_2 is not empty
        if text_2:
            img = sample_image.copy()
            draw = ImageDraw.Draw(img)
            font = get_fit_font(draw, text_2, img.size, base_font_size)
            bbox = draw.textbbox((0, 0), text_2, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (img.size[0] - text_width) // 2
            y = (img.size[1] - text_height) // 2
            draw.text((x, y), text_2, font=font, fill="black", align="center")
            img.save(os.path.join(folder_path, f"image_column_5_{i}.png"))
            log(f"Saved image from 'column_5' for Record {i + 1} in {folder_path}.")

    log("Image generation complete.")
