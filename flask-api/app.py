import os
import torch
import torchvision
from torch.utils.data import DataLoader
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.transforms import functional as F
import matplotlib.pyplot as plt
from PIL import Image
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Model setup
def get_model(num_classes):
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

# Initialize model
num_classes = 2  # Background + leaf
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model = get_model(num_classes)
model.load_state_dict(torch.load("fasterrcnn_resnet50_epoch_9.pth", map_location=device))
model.to(device)
model.eval()

COCO_CLASSES = {0: "Background", 1: "Leaf"}

def get_class_name(class_id):
    return COCO_CLASSES.get(class_id, "Unknown")

def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = F.to_tensor(image).unsqueeze(0)
    return image_tensor.to(device), image

def draw_boxes(image, prediction):
    plt.figure(figsize=(12, 10))
    plt.imshow(image)
    plt.axis('off')
    
    boxes = prediction[0]['boxes'].cpu().numpy()
    labels = prediction[0]['labels'].cpu().numpy()
    scores = prediction[0]['scores'].cpu().numpy()
    
    threshold = 0.86
    detected_leaves = sum(1 for score in scores if score > threshold)

    # Draw bounding boxes
    ax = plt.gca()
    for box, label, score in zip(boxes, labels, scores):
        if score > threshold:
            x_min, y_min, x_max, y_max = box
            class_name = get_class_name(label)
            ax.add_patch(plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                                     linewidth=2, edgecolor='r', facecolor='none'))
            ax.text(x_min, y_min, f"{class_name} ({score:.2f})", color='r', fontsize=12,
                   bbox=dict(facecolor='white', alpha=0.5))

    plt.text(image.width // 2, 20, f"Number of Leaves: {detected_leaves}", color='red',
             fontsize=18, fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8))
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf, detected_leaves

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process image with model
            try:
                image_tensor, image = process_image(filepath)
                with torch.no_grad():
                    prediction = model(image_tensor)
                
                # Generate output image with boxes
                img_buf, leaf_count = draw_boxes(image, prediction)
                img_str = base64.b64encode(img_buf.getvalue()).decode()
                
                # Clean up
                os.remove(filepath)
                
                return render_template('index.html', 
                                     result_image=img_str,
                                     leaf_count=leaf_count)
            
            except Exception as e:
                return render_template('index.html', 
                                     error=f'Error processing image: {str(e)}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)