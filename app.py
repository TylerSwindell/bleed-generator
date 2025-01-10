from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageOps
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BLEED_FOLDER = "bleeds"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BLEED_FOLDER, exist_ok=True)

# Conversion factors
PIXELS_PER_INCH = 300
PIXELS_PER_CM = 118


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle the uploaded image
        image_file = request.files["image"]
        bleed_width = float(request.form.get("bleed_width", 0))
        unit = request.form.get("unit", "pixels")
        crop_marks = request.form.get("crop_marks", "off") == "on"
        # bleed_stretch = int(request.form.get("bleed_stretch", 10))
        crop_mark_width = int(request.form.get("crop_mark_width", 1))
        crop_mark_length = int(request.form.get("crop_mark_length", 10))

        if unit == "inches":
            bleed_width = int(bleed_width * PIXELS_PER_INCH)
        elif unit == "cm":
            bleed_width = int(bleed_width * PIXELS_PER_CM)
        else:
            bleed_width = int(bleed_width)

        if image_file and bleed_width > 0:
            filename = os.path.join(UPLOAD_FOLDER, image_file.filename)
            image_file.save(filename)

            # Process image to create bleed
            output_path = os.path.join(BLEED_FOLDER, f"bleed_{image_file.filename}")
            create_image_bleed(
                filename,
                bleed_width,
                crop_marks,
                # bleed_stretch,
                crop_mark_width,
                crop_mark_length,
                output_path,
            )

            return send_file(output_path, mimetype="image/png", as_attachment=True)

    return render_template("index.html")


def create_image_bleed(
    input_path,
    bleed_width,
    crop_marks,
    # bleed_stretch,
    crop_mark_width,
    crop_mark_length,
    output_path,
):
    """Generates an image with bleeds around its edges and optional crop marks."""
    image = Image.open(input_path)
    width, height = image.size

    # Calculate canvas size including crop marks
    crop_mark_length = max(5, crop_mark_length) if crop_marks else 0
    new_width = width + 2 * (bleed_width + crop_mark_length)
    new_height = height + 2 * (bleed_width + crop_mark_length)
    canvas = Image.new("RGB", (new_width, new_height), (255, 255, 255))

    # Paste the original image in the center, accounting for bleed and crop mark extension
    paste_x = bleed_width + crop_mark_length
    paste_y = bleed_width + crop_mark_length
    canvas.paste(image, (paste_x, paste_y))

    # Create and paste stretched edge bleeds
    edges = {
        "top": image.crop((0, 0, width, 1))
        .resize((width, bleed_width))
        .crop((0, 0, width, bleed_width)),
        "bottom": image.crop((0, height - 1, width, height))
        .resize((width, bleed_width))
        .crop((0, 0, width, bleed_width)),
        "left": image.crop((0, 0, 1, height))
        .resize((bleed_width, height))
        .crop((0, 0, bleed_width, height)),
        "right": image.crop((width - 1, 0, width, height))
        .resize((bleed_width, height))
        .crop((0, 0, bleed_width, height)),
    }

    canvas.paste(edges["top"], (paste_x, crop_mark_length))
    canvas.paste(edges["bottom"], (paste_x, height + paste_y))
    canvas.paste(edges["left"], (crop_mark_length, paste_y))
    canvas.paste(edges["right"], (width + paste_x, paste_y))

    # Create and paste corner bleeds
    corners = {
        "top_left": image.crop((0, 0, 1, 1))
        .resize((bleed_width, bleed_width))
        .crop((0, 0, bleed_width, bleed_width)),
        "top_right": image.crop((width - 1, 0, width, 1))
        .resize((bleed_width, bleed_width))
        .crop((0, 0, bleed_width, bleed_width)),
        "bottom_left": image.crop((0, height - 1, 1, height))
        .resize((bleed_width, bleed_width))
        .crop((0, 0, bleed_width, bleed_width)),
        "bottom_right": image.crop((width - 1, height - 1, width, height))
        .resize((bleed_width, bleed_width))
        .crop((0, 0, bleed_width, bleed_width)),
    }

    canvas.paste(corners["top_left"], (crop_mark_length, crop_mark_length))
    canvas.paste(corners["top_right"], (width + paste_x, crop_mark_length))
    canvas.paste(corners["bottom_left"], (crop_mark_length, height + paste_y))
    canvas.paste(corners["bottom_right"], (width + paste_x, height + paste_y))

    # Add crop marks if enabled
    if crop_marks:
        draw = ImageDraw.Draw(canvas)

        # Top-left corner
        draw.line(
            [
                (
                    paste_x,
                    crop_mark_length,
                ),
                (
                    paste_x,
                    0,
                ),
            ],
            fill="black",
            width=crop_mark_width,
        )
        draw.line(
            [
                (crop_mark_length, paste_y),
                (0, paste_y),
            ],
            fill="black",
            width=crop_mark_width,
        )

        # Top-right corner
        draw.line(
            [
                (width + paste_x, crop_mark_length),
                (
                    width + paste_x,
                    0,
                ),
            ],
            fill="black",
            width=crop_mark_width,
        )
        draw.line(
            [
                (width + paste_x + bleed_width + crop_mark_length, paste_y),
                (width + paste_x + bleed_width, paste_y),
            ],
            fill="black",
            width=crop_mark_width,
        )

        # Bottom-left corner
        draw.line(
            [
                (paste_x, height + paste_y + bleed_width),
                (paste_x, height + paste_y + bleed_width + crop_mark_length),
            ],
            fill="black",
            width=crop_mark_width,
        )
        draw.line(
            [
                (paste_x - bleed_width, height + paste_y),
                (
                    0,
                    height + paste_y,
                ),
            ],
            fill="black",
            width=crop_mark_width,
        )

        # Bottom-right corner
        draw.line(
            [
                (width + paste_x, new_height - crop_mark_length),
                (
                    width + paste_x,
                    new_height + crop_mark_length,
                ),
            ],
            fill="black",
            width=crop_mark_width,
        )
        draw.line(
            [
                (new_width - crop_mark_length, height + paste_y),
                (new_width + crop_mark_length, height + paste_y),
            ],
            fill="black",
            width=crop_mark_width,
        )

    # Save the output
    canvas.save(output_path, "PNG")


if __name__ == "__main__":
    app.run(debug=True)
