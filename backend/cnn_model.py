# backend/cnn_model.py

import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

# Path to your trained multi-class model (.h5)
MODEL_PATH = r"D:\cnn_model_final.h5"

try:
    print("🔍 Loading CNN model...")
    cnn_model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ CNN model loaded successfully")
except Exception as e:
    print("❌ Error loading CNN model:", e)
    cnn_model = None


# Image size used during training
IMG_SIZE = (150, 150)
 
CLASS_NAMES = [
    "Apple Scab",                                        # 0
    "Apple Black Rot",                                   # 1
    "Apple Cedar Apple Rust",                            # 2
    "Apple Healthy",                                     # 3
    "Blueberry Healthy",                                 # 4
    "Cherry Healthy",                                    # 5
    "Cherry Powdery Mildew",                             # 6
    "Corn Gray Leaf Spot",                               # 7
    "Corn Common Rust",                                  # 8
    "Corn Healthy",                                      # 9
    "Corn Northern Leaf Blight",                         # 10
    "Grape Black Rot",                                   # 11
    "Grape Esca (Black Measles)",                        # 12
    "Grape Healthy",                                     # 13
    "Grape Leaf Blight (Isariopsis Leaf Spot)",          # 14
    "Citrus Greening (Huanglongbing)",                   # 15
    "Peach Bacterial Spot",                              # 16
    "Peach Healthy",                                     # 17
    "Pepper Bacterial Spot",                             # 18
    "Pepper Healthy",                                    # 19
    "Potato Early Blight",                               # 20
    "Potato Healthy",                                    # 21
    "Potato Late Blight",                                # 22
    "Raspberry Healthy",                                 # 23
    "Soybean Healthy",                                   # 24
    "Squash Powdery Mildew",                             # 25
    "Strawberry Healthy",                                # 26
    "Strawberry Leaf Scorch",                            # 27
    "Tomato Bacterial Spot",                             # 28
    "Tomato Early Blight",                               # 29
    "Tomato Healthy",                                    # 30
    "Tomato Late Blight",                                # 31
    "Tomato Leaf Mold",                                  # 32
    "Tomato Septoria Leaf Spot",                         # 33
    "Tomato Spider Mite (Two-spotted)",                  # 34
    "Tomato Target Spot",                                # 35
    "Tomato Mosaic Virus",                               # 36
    "Tomato Yellow Leaf Curl Virus"                      # 37
]


def preprocess_image(image_bytes):
    """Convert uploaded image bytes → preprocessed array for the model."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_image(image_bytes):
    """
    Run prediction using the CNN model.

    Supports:
    - Multi-class softmax output: shape (1, N)
    - Binary sigmoid output: shape (1, 1)

    Returns:
    {
      "prediction": <int>,          # class index or 0/1
      "class_name": <str>,          # best text label if available
      "confidence": <float>         # probability of predicted class
    }
    """
    if cnn_model is None:
        return {"error": "Model not loaded"}

    processed = preprocess_image(image_bytes)
    prediction = cnn_model.predict(processed)

    # Multi-class: shape (1, N) with N > 1
    if prediction.ndim == 2 and prediction.shape[1] > 1:
        probs = prediction[0]  # shape (N,)
        class_index = int(np.argmax(probs))
        confidence = float(np.max(probs))

        # Map index → name if we have it, else generic name
        if 0 <= class_index < len(CLASS_NAMES):
            class_name = CLASS_NAMES[class_index]
        else:
            class_name = f"class_{class_index}"

        return {
            "prediction": class_index,
            "class_name": class_name,
            "confidence": confidence,
        }

    # Binary case: shape (1, 1) – kept for backward compatibility
    prob = float(prediction[0][0])
    label = int(prob > 0.5)
    class_name = "Apple Scab" if label == 1 else "Healthy"

    return {
        "prediction": label,
        "class_name": class_name,
        "confidence": prob,
    }
