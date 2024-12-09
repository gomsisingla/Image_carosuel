from flask import Flask, request, jsonify, send_from_directory
import os
import uuid

app = Flask(__name__)

# Path to save uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Function to save uploaded image
@app.route("/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file with a unique name
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "file_path": file_path})

# Save edited image from frontend
@app.route("/save_image", methods=["POST"])
def save_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Define the path to save the image
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(save_path)

    return jsonify({"message": "Image saved successfully", "file_path": save_path})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
