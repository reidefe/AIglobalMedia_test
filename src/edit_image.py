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
    and saves them in a folder named after another column.

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

    # Set fonts
    try:
        font = ImageFont.truetype("arial.ttf", size=40)
    except Exception as e:
        log(f"Error loading font: {e}")
        return

    data_to_process = data.head(row_limit) if row_limit > 0 else data
    log(f"Processing {len(data_to_process)} records for image generation...")

    for i, row in data_to_process.iterrows():
        # Extract folder name and image texts
        folder_name = str(row.get("Column_5", "")).strip()
        text_1 = str(row.get("Column_3", "")).strip()
        text_2 = str(row.get("Column_6", "")).strip()

        # Skip rows only if any of these critical fields are missing
        if not folder_name:
            log(f"Skipping Record {i}: Missing folder name (column_2).")
            continue

        if not text_1 and not text_2:
            log(f"Skipping Record {i}: Both text fields (column_3 and column_5) are empty.")
            continue

        log(f"Record {i}: Creating folder '{folder_name}' and generating images.")

        # Create the folder for the domain
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Generate the first image if text_1 is not empty
        if text_1:
            img = sample_image.copy()
            draw = ImageDraw.Draw(img)
            text_bbox = draw.textbbox((0, 0), text_1, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            x = (img.size[0] - text_width) // 2
            y = (img.size[1] - text_height) // 2
            draw.text((x, y), text_1, font=font, fill="black", align="center")
            img.save(os.path.join(folder_path, f"image_column_3_{i}.png"))
            log(f"Saved image from 'column_3' for Record {i} in {folder_path}.")

        # Generate the second image if text_2 is not empty
        if text_2:
            img = sample_image.copy()
            draw = ImageDraw.Draw(img)
            text_bbox = draw.textbbox((0, 0), text_2, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            x = (img.size[0] - text_width) // 2
            y = (img.size[1] - text_height) // 2
            draw.text((x, y), text_2, font=font, fill="black", align="center")
            img.save(os.path.join(folder_path, f"image_column_5_{i}.png"))
            log(f"Saved image from 'column_5' for Record {i} in {folder_path}.")

    log("Image generation complete.")
