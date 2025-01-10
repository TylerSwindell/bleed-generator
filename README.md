# Image Bleed Generator Web App

This web application generates image bleeds for print-ready PDFs. Users can upload an image, specify the bleed size, toggle crop marks, and download the processed image. The app supports customizing crop mark distance, length, and width for added flexibility.

## Features

- Generate image bleeds by stretching and cropping edges.
- Add crop marks to demarcate bleed and image boundaries.
- Customize bleed size in pixels, inches, or centimeters.
- Adjust crop mark distance, length, and width.
- Preview the generated image and download the result.

---

## Components

### 1. **Backend (Flask)**

The Flask server handles:

- Image uploads and processing.
- Generating image bleeds by mirroring and stretching edges.
- Adding optional crop marks based on user configurations.

#### Key Files

- **`app.py`**:
  - Manages routes (`/`) and file uploads.
  - Processes images using the Python Imaging Library (Pillow).
  - Handles user inputs for bleed size, crop mark properties, and units.
- **Dependencies**:
  - `Flask` for server operations.
  - `Pillow` for image manipulation.

#### Endpoints

- **`GET /`**: Serves the web interface.
- **`POST /`**: Processes the uploaded image and returns the result.

---

### 2. **Frontend (HTML)**

The user interface is a simple form that:

- Allows image uploads.
- Collects user inputs for bleed size and crop mark options.
- Submits the form to the Flask backend for processing.

#### Key Features

- Form elements:
  - File input for image uploads.
  - Fields for bleed width, unit selection, crop mark distance, width, and length.
  - Toggle for enabling/disabling crop marks.

---

## Development Guide

### Prerequisites

- Python 3.8+
- `pip` package manager

### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app locally:
   ```bash
   python app.py
   ```
4. Access the app at `http://127.0.0.1:5000`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
