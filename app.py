from flask import Flask, render_template_string, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

# Modern UI Theme with Image Grid
UI_THEME = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Image Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6C63FF;
            --secondary: #4D44DB;
            --accent: #FF6584;
            --light: #F8F9FA;
            --dark: #212529;
            --gray: #6C757D;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            min-height: 100vh;
            color: var(--dark);
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        header {
            background: var(--primary);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-section {
            background: white;
            border: 2px dashed var(--primary);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 40px;
            transition: all 0.3s;
        }
        
        .upload-section:hover {
            border-color: var(--accent);
            box-shadow: 0 10px 30px rgba(108, 99, 255, 0.2);
        }
        
        .upload-icon {
            font-size: 3rem;
            color: var(--primary);
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            color: var(--secondary);
        }
        
        input[type="file"] {
            display: none;
        }
        
        .custom-file-upload {
            border: 2px solid var(--primary);
            color: var(--primary);
            display: inline-block;
            padding: 12px 24px;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        
        .custom-file-upload:hover {
            background: var(--primary);
            color: white;
        }
        
        .preview-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .prompt-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .prompt-input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2);
        }
        
        .generate-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .generate-btn:hover {
            background: var(--secondary);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(108, 99, 255, 0.3);
        }
        
        .results-section {
            display: none;
            margin-top: 40px;
        }
        
        .section-title {
            font-size: 1.8rem;
            margin-bottom: 30px;
            color: var(--secondary);
            text-align: center;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .image-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .image-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .card-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        
        .card-body {
            padding: 20px;
        }
        
        .card-title {
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: var(--dark);
        }
        
        .card-desc {
            color: var(--gray);
            margin-bottom: 15px;
            font-size: 0.9rem;
        }
        
        .download-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .download-btn:hover {
            background: #e65571;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 40px 0;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(108, 99, 255, 0.2);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 1s ease-in-out infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .content {
                padding: 20px;
            }
            
            .image-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Image Generator</h1>
            <p class="subtitle">Transform your images with AI magic</p>
        </header>
        
        <div class="content">
            <div class="upload-section">
                <div class="upload-icon">🖼️</div>
                <h2>Upload Your Image</h2>
                <p>Start by uploading an image and entering your creative prompt</p>
                
                <form id="uploadForm" method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="fileInput">Choose an image</label>
                        <label for="fileInput" class="custom-file-upload">
                            Select Image
                        </label>
                        <input id="fileInput" type="file" name="image" accept="image/*" required>
                        <img id="imagePreview" class="preview-image" src="#" alt="Preview">
                    </div>
                    
                    <div class="form-group">
                        <label for="prompt">Your Creative Prompt</label>
                        <input type="text" id="prompt" name="prompt" class="prompt-input" 
                               placeholder="Ex: 'Transform this into a cyberpunk style'" required>
                    </div>
                    
                    <button type="submit" class="generate-btn">Generate AI Variations</button>
                </form>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3>Generating your AI images...</h3>
                <p>This may take a few moments</p>
            </div>
            
            <div class="results-section" id="results">
                <h2 class="section-title">Your AI Generated Images</h2>
                <div class="image-grid" id="imageGrid">
                    <!-- Original image card -->
                    <div class="image-card">
                        <img src="{{ original_image }}" class="card-image" alt="Original Image">
                        <div class="card-body">
                            <h3 class="card-title">Original Image</h3>
                            <p class="card-desc">Your uploaded image</p>
                        </div>
                    </div>
                    
                    <!-- Generated image cards will be added here by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // Preview uploaded image
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('imagePreview').src = event.target.result;
                    document.getElementById('imagePreview').style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
        
        // Show loading animation when form is submitted
        document.getElementById('uploadForm').addEventListener('submit', function() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
        });
        
        // In a real app, you would have AJAX code here to fetch generated images
        // This is just a simulation for the UI
        {% if generated_images %}
            document.addEventListener('DOMContentLoaded', function() {
                const imageGrid = document.getElementById('imageGrid');
                
                // Add generated images to the grid
                {% for img in generated_images %}
                    const card = document.createElement('div');
                    card.className = 'image-card';
                    card.innerHTML = `
                        <img src="{{ img.url }}" class="card-image" alt="Generated Image {{ loop.index }}">
                        <div class="card-body">
                            <h3 class="card-title">Variation {{ loop.index }}</h3>
                            <p class="card-desc">{{ img.prompt }}</p>
                            <a href="{{ img.url }}" download class="download-btn">Download</a>
                        </div>
                    `;
                    imageGrid.appendChild(card);
                {% endfor %}
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').style.display = 'block';
            });
        {% endif %}
    </script>
</body>
</html>
"""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'image' not in request.files:
            return "No image uploaded", 400
        
        image_file = request.files['image']
        prompt = request.form.get('prompt', '')
        
        if image_file.filename == '':
            return "No selected file", 400
        
        if image_file and allowed_file(image_file.filename):
            # Save original image
            filename = secure_filename(image_file.filename)
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(original_path)
            
            # In a real app, you would generate AI images here
            # For demo purposes, we'll create mock generated images
            generated_images = []
            for i in range(1, 6):
                # This would be replaced with actual AI generation code
                # For now, we'll just create variations of the original
                img = cv2.imread(original_path)
                
                # Apply different effects to create "variations"
                if i == 1:
                    img = cv2.stylization(img, sigma_s=60, sigma_r=0.6)  # Watercolor effect
                elif i == 2:
                    img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)  # Detailed
                elif i == 3:
                    img = cv2.edgePreservingFilter(img, flags=1, sigma_s=64, sigma_r=0.2)  # Edge preserving
                elif i == 4:
                    h, w = img.shape[:2]
                    noise = np.random.randint(0, 50, (h, w, 3), dtype=np.uint8)
                    img = cv2.addWeighted(img, 0.7, noise, 0.3, 0)  # Noisy
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Grayscale
                
                # Save generated image
                gen_filename = f"generated_{i}_{filename}"
                gen_path = os.path.join(app.config['UPLOAD_FOLDER'], gen_filename)
                cv2.imwrite(gen_path, img)
                
                generated_images.append({
                    'url': url_for('static', filename=f'uploads/{gen_filename}'),
                    'prompt': f"{prompt} (variation {i})"
                })
            
            return render_template_string(UI_THEME, 
                                       original_image=url_for('static', filename=f'uploads/{filename}'),
                                       generated_images=generated_images)
    
    return render_template_string(UI_THEME)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
