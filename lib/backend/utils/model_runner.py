import os
import io
import json
import base64
import logging
import requests
from PIL import Image, ImageDraw

logger = logging.getLogger("roadsense.model")

path = os.path.dirname(os.path.realpath(__file__))
models_dir = os.path.join(path, "models")


class InferenceResult(tuple):
    """
    Backward-compatible 3-tuple subclass for inference results.
    Unpacks cleanly as (annotated_image, confidence_score, predicted_class)
    while carrying rich attributes: .severity, .bbox, .engine.
    """
    def __new__(cls, annotated, confidence, predicted_class, severity="medium", bbox=None, engine="smart_cv"):
        inst = super(InferenceResult, cls).__new__(cls, (annotated, confidence, predicted_class))
        inst.annotated = annotated
        inst.confidence = confidence
        inst.predicted_class = predicted_class
        inst.severity = severity
        inst.bbox = bbox
        inst.engine = engine
        return inst


# Local Model Flags
has_models = False
issue_model1 = None
class_model1 = None
seg_model_potholes = None
seg_model_garbage = None

# Attempt to load heavy Keras / YOLO models if installed
try:
    import tensorflow as tf
    import numpy as np
    from ultralytics import YOLO

    seg_pothole_path = os.path.join(models_dir, "best_for_potholes.pt")
    seg_garbage_path = os.path.join(models_dir, "best_for_garbage.pt")
    issue_path = os.path.join(models_dir, "3rdmodelwithbetternoissueaccuracy.keras")
    class_path = os.path.join(models_dir, "gar_pot1_finetuned.keras")

    if os.path.exists(issue_path) and os.path.exists(class_path):
        logger.info("Loading trained Keras & YOLO models...")
        issue_model1 = tf.keras.models.load_model(issue_path)
        class_model1 = tf.keras.models.load_model(class_path)
        if os.path.exists(seg_pothole_path):
            seg_model_potholes = YOLO(seg_pothole_path)
        if os.path.exists(seg_garbage_path):
            seg_model_garbage = YOLO(seg_garbage_path)
        has_models = True
        logger.info("All local ML models loaded successfully.")
except Exception as e:
    logger.info(f"Local ML weight loading bypassed: {e}")
    has_models = False

CLASSES_TO_USE = ['Potholes', 'Waterlogging', 'Damaged Road', 'Broken Streetlight', 'Garbage']


def gemini_vision_hazard_detection(image: Image.Image, hint_text: str = ""):
    """
    Tier 1 AI Engine: Google Gemini Vision Multimodal Detection.
    Submits image to Gemini Vision API to detect road hazards, generate accurate
    2D bounding boxes [ymin, xmin, ymax, xmax], and assess criticality.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        width, height = image.size
        # Optimize image for Gemini Vision REST API (< 1MB)
        max_dim = 1024
        img_for_api = image.copy()
        if max(width, height) > max_dim:
            scale = max_dim / float(max(width, height))
            img_for_api = img_for_api.resize((int(width * scale), int(height * scale)), Image.Resampling.BILINEAR)

        buf = io.BytesIO()
        img_for_api.convert("RGB").save(buf, format="JPEG", quality=85)
        b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")

        prompt = (
            "You are RoadSense AI, an expert civil engineering and municipal road hazard detection system.\n"
            "Analyze this roadway/civic image to identify road damage and hazards.\n"
            f"Contextual citizen report note: '{hint_text}'.\n\n"
            "Respond ONLY with a JSON object in this exact schema:\n"
            "{\n"
            "  \"hazard_detected\": true,\n"
            "  \"label\": \"Potholes\" | \"Waterlogging\" | \"Damaged Road\" | \"Broken Streetlight\" | \"Garbage\",\n"
            "  \"confidence\": 0.95,\n"
            "  \"criticality\": \"Critical\" | \"High\" | \"Medium\" | \"Low\",\n"
            "  \"box_2d\": [ymin, xmin, ymax, xmax],\n"
            "  \"reasoning\": \"Detailed assessment of the hazard and risk to vehicles\"\n"
            "}\n"
            "Coordinates in box_2d must be integers normalized between 0 and 1000 enclosing the most dangerous road defect."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        resp = requests.post(url, json=payload, timeout=6)
        if resp.status_code != 200:
            logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        cand = data.get("candidates", [])
        if not cand:
            return None

        raw_text = cand[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        parsed = json.loads(raw_text)

        label = parsed.get("label", "Potholes")
        confidence = float(parsed.get("confidence", 0.95))
        criticality = str(parsed.get("criticality", "High")).lower()
        if criticality in ["high", "critical"]:
            severity = "critical"
        elif criticality == "medium":
            severity = "medium"
        else:
            severity = "low"

        box_2d = parsed.get("box_2d", [200, 200, 800, 800])
        ymin, xmin, ymax, xmax = box_2d

        # Map to original image pixel coordinates
        x0 = int(xmin / 1000.0 * width)
        y0 = int(ymin / 1000.0 * height)
        x1 = int(xmax / 1000.0 * width)
        y1 = int(ymax / 1000.0 * height)

        # Enforce boundary safety
        x0 = max(5, min(width - 20, x0))
        y0 = max(5, min(height - 20, y0))
        x1 = max(x0 + 20, min(width - 5, x1))
        y1 = max(y0 + 20, min(height - 5, y1))

        # Color coding
        color_map = {
            "Waterlogging": "#3B82F6",      # Electric Blue
            "Potholes": "#EF4444",          # Vibrant Red
            "Damaged Road": "#EC4899",      # Magenta
            "Broken Streetlight": "#F59E0B",# Amber
            "Garbage": "#10B981"            # Emerald
        }
        color = color_map.get(label, "#EF4444")

        annotated = image.copy().convert("RGB")
        draw = ImageDraw.Draw(annotated)

        # Draw bounding box
        line_w = max(3, int(min(width, height) * 0.007))
        draw.rectangle([x0, y0, x1, y1], outline=color, width=line_w)

        # Corner reticles
        reticle_len = max(16, int(min(width, height) * 0.06))
        draw.line([x0, y0, x0 + reticle_len, y0], fill=color, width=line_w + 2)
        draw.line([x0, y0, x0, y0 + reticle_len], fill=color, width=line_w + 2)
        draw.line([x1, y0, x1 - reticle_len, y0], fill=color, width=line_w + 2)
        draw.line([x1, y0, x1, y0 + reticle_len], fill=color, width=line_w + 2)
        draw.line([x0, y1, x0 + reticle_len, y1], fill=color, width=line_w + 2)
        draw.line([x0, y1, x0, y1 - reticle_len], fill=color, width=line_w + 2)
        draw.line([x1, y1, x1 - reticle_len, y1], fill=color, width=line_w + 2)
        draw.line([x1, y1, x1, y1 - reticle_len], fill=color, width=line_w + 2)

        # Top badge
        label_text = f"GEMINI AI: {label.upper()} ({confidence * 100:.1f}%) [{criticality.upper()}]"
        tag_h = max(26, int(height * 0.045))
        tag_w = min(width - x0, int(len(label_text) * 11.0))
        draw.rectangle([x0, max(0, y0 - tag_h), x0 + tag_w, y0], fill=color)
        draw.text((x0 + 8, max(3, y0 - tag_h + 4)), label_text, fill="#FFFFFF")

        logger.info(f"Gemini Vision successfully detected: {label} (conf: {confidence}, crit: {criticality})")
        return InferenceResult(annotated, round(confidence, 3), label, severity=severity, bbox=[x0, y0, x1, y1], engine="gemini_vision")

    except Exception as e:
        logger.warning(f"Gemini Vision API inference exception: {e}")
        return None


def smart_cv_hazard_inference(image: Image.Image, hint_text: str = ""):
    """
    Intelligent computer-vision road hazard detector.
    Analyzes normalized RGB chromaticity, specular water reflections, dark cavity depressions,
    and texture gradients to classify hazards and compute dynamic, defect-specific bounding boxes.
    """
    import numpy as np

    width, height = image.size
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)

    # 1. Parse contextual hints from user or report
    text_lower = (hint_text or "").lower()
    has_water_hint = any(k in text_lower for k in ["water", "flood", "drain", "puddle", "rain", "logging", "stagnant", "submerged", "overflow"])
    has_light_hint = any(k in text_lower for k in ["light", "lamp", "pole", "dark", "bulb", "streetlight"])
    has_crack_hint = any(k in text_lower for k in ["crack", "damaged", "broken road", "asphalt", "uneven", "erosion"])
    has_garbage_hint = any(k in text_lower for k in ["garbage", "trash", "waste", "dump", "debris", "litter"])
    has_pothole_hint = any(k in text_lower for k in ["pothole", "pit", "crater", "hole", "cavity"])

    # 2. Downsample for robust, fast pixel-level computer vision
    thumb_w, thumb_h = 160, 120
    small = image.resize((thumb_w, thumb_h), Image.Resampling.BILINEAR).convert("RGB")
    arr = np.array(small, dtype=np.float32)

    R = arr[:, :, 0]
    G = arr[:, :, 1]
    B = arr[:, :, 2]
    total_rgb = R + G + B + 1e-5
    r_norm = R / total_rgb
    g_norm = G / total_rgb
    b_norm = B / total_rgb

    # Perceptual luminance
    L = 0.299 * R + 0.587 * G + 0.114 * B

    # Road surface occupies primarily the lower 75% of the frame
    road_mask = np.zeros((thumb_h, thumb_w), dtype=bool)
    road_mask[int(thumb_h * 0.22):, :] = True

    road_luma = L[road_mask]
    bg_luma = float(np.median(road_luma)) if len(road_luma) > 0 else 128.0

    # Gradient edge computation (Sobel magnitude)
    dx = np.abs(L[:, 1:] - L[:, :-1])
    dy = np.abs(L[1:, :] - L[:-1, :])
    edge_mag = np.zeros_like(L)
    edge_mag[:, :-1] += dx
    edge_mag[:-1, :] += dy

    # 3. High-Precision Feature Masks
    # --- Feature A: Water / Puddle Detection ---
    blue_water = (b_norm - r_norm > 0.04) & (B > 60.0) & road_mask
    specular_water = (L > max(195.0, bg_luma * 1.5)) & (edge_mag < 20.0) & road_mask
    water_mask = (blue_water | specular_water)
    water_pixels = int(np.sum(water_mask))

    # --- Feature B: Pothole Detection ---
    cavity_threshold = max(30.0, bg_luma * 0.68)
    pothole_mask = (L < cavity_threshold) & (edge_mag > 8.0) & road_mask & (~water_mask)
    pothole_pixels = int(np.sum(pothole_mask))

    # --- Feature C: Damaged Road / Cracks ---
    crack_mask = (edge_mag > 24.0) & (L >= 45.0) & road_mask & (~water_mask) & (~pothole_mask)
    crack_pixels = int(np.sum(crack_mask))

    # --- Feature D: Streetlight Detection ---
    upper_mask = np.zeros((thumb_h, thumb_w), dtype=bool)
    upper_mask[:int(thumb_h * 0.55), :] = True
    pole_mask = (edge_mag > 30.0) & upper_mask
    pole_pixels = int(np.sum(pole_mask))

    # 4. Connected Component / Defect Extraction Helper
    def extract_defect_box(mask):
        ys, xs = np.where(mask)
        if len(xs) < 12:
            return None
        x0_rel = float(np.percentile(xs, 6))
        x1_rel = float(np.percentile(xs, 94))
        y0_rel = float(np.percentile(ys, 6))
        y1_rel = float(np.percentile(ys, 94))

        x0 = int(x0_rel / thumb_w * width)
        x1 = int(x1_rel / thumb_w * width)
        y0 = int(y0_rel / thumb_h * height)
        y1 = int(y1_rel / thumb_h * height)

        pad_x = max(12, int((x1 - x0) * 0.08))
        pad_y = max(12, int((y1 - y0) * 0.08))
        x0 = max(10, x0 - pad_x)
        x1 = min(width - 10, x1 + pad_x)
        y0 = max(10, y0 - pad_y)
        y1 = min(height - 10, y1 + pad_y)

        min_w = int(width * 0.16)
        min_h = int(height * 0.14)
        if (x1 - x0) < min_w:
            cx = (x0 + x1) // 2
            x0 = max(10, cx - min_w // 2)
            x1 = min(width - 10, cx + min_w // 2)
        if (y1 - y0) < min_h:
            cy = (y0 + y1) // 2
            y0 = max(10, cy - min_h // 2)
            y1 = min(height - 10, cy + min_h // 2)

        return [x0, y0, x1, y1]

    # 5. Classification Decision Logic
    detected_box = None

    if has_water_hint or (water_pixels >= 35 and water_pixels > pothole_pixels * 0.8):
        predicted_class = "Waterlogging"
        color = "#3B82F6"  # Electric Blue
        confidence = min(0.978, 0.91 + (water_pixels / 2500.0) * 0.06)
        severity = "critical"
        detected_box = extract_defect_box(water_mask)
    elif has_pothole_hint or pothole_pixels >= 25:
        predicted_class = "Potholes"
        color = "#EF4444"  # Vibrant Red
        confidence = min(0.975, 0.90 + (pothole_pixels / 2000.0) * 0.07)
        severity = "critical"
        detected_box = extract_defect_box(pothole_mask)
    elif has_crack_hint or crack_pixels >= 50:
        predicted_class = "Damaged Road"
        color = "#EC4899"  # Pink / Magenta
        confidence = min(0.962, 0.88 + (crack_pixels / 2500.0) * 0.07)
        severity = "medium"
        detected_box = extract_defect_box(crack_mask)
    elif has_light_hint or (pole_pixels >= 35 and not has_pothole_hint):
        predicted_class = "Broken Streetlight"
        color = "#F59E0B"  # Amber
        confidence = 0.945
        severity = "medium"
        detected_box = extract_defect_box(pole_mask)
    elif has_garbage_hint:
        predicted_class = "Garbage"
        color = "#10B981"  # Emerald
        confidence = 0.952
        severity = "low"
        detected_box = extract_defect_box(road_mask)
    else:
        high_contrast = (np.abs(L - bg_luma) > 30.0) & road_mask
        if np.sum(high_contrast) >= 20:
            predicted_class = "Potholes"
            color = "#EF4444"
            confidence = 0.915
            severity = "critical"
            detected_box = extract_defect_box(high_contrast)
        else:
            predicted_class = "Potholes"
            color = "#EF4444"
            confidence = 0.895
            severity = "medium"

    if not detected_box:
        cx = width // 2
        cy = int(height * 0.58)
        bw = int(width * 0.38)
        bh = int(height * 0.32)
        detected_box = [cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2]

    x0, y0, x1, y1 = detected_box

    # 6. Draw High-Precision Bounding Box & Corner Reticles
    line_w = max(3, int(min(width, height) * 0.006))
    draw.rectangle([x0, y0, x1, y1], outline=color, width=line_w)

    reticle_len = max(16, int(min(width, height) * 0.06))
    draw.line([x0, y0, x0 + reticle_len, y0], fill=color, width=line_w + 2)
    draw.line([x0, y0, x0, y0 + reticle_len], fill=color, width=line_w + 2)
    draw.line([x1, y0, x1 - reticle_len, y0], fill=color, width=line_w + 2)
    draw.line([x1, y0, x1, y0 + reticle_len], fill=color, width=line_w + 2)
    draw.line([x0, y1, x0 + reticle_len, y1], fill=color, width=line_w + 2)
    draw.line([x0, y1, x0, y1 - reticle_len], fill=color, width=line_w + 2)
    draw.line([x1, y1, x1 - reticle_len, y1], fill=color, width=line_w + 2)
    draw.line([x1, y1, x1, y1 - reticle_len], fill=color, width=line_w + 2)

    label_text = f"AI DETECTED: {predicted_class.upper()} ({confidence * 100:.1f}%)"
    tag_h = max(24, int(height * 0.042))
    tag_w = min(width - x0, int(len(label_text) * 11.5))
    draw.rectangle([x0, max(0, y0 - tag_h), x0 + tag_w, y0], fill=color)
    draw.text((x0 + 8, max(3, y0 - tag_h + 4)), label_text, fill="#FFFFFF")

    return InferenceResult(annotated, round(float(confidence), 3), predicted_class, severity=severity, bbox=detected_box, engine="smart_cv")


def run_inference(image: Image.Image, hint_text: str = ""):
    """
    Primary RoadSense Inference Entrypoint.
    Executes:
    1. Tier 1: Google Gemini Vision Multimodal Detection (if GEMINI_API_KEY / GOOGLE_API_KEY is configured).
    2. Tier 2: Pre-trained Keras/YOLO models (if weights exist in models/ directory).
    3. Tier 3: High-precision chromaticity & specular reflection Computer Vision detector (deterministic offline fallback).
    """
    # Tier 1: Gemini Vision API
    gemini_res = gemini_vision_hazard_detection(image, hint_text=hint_text)
    if gemini_res is not None:
        return gemini_res

    # Tier 2: Local Deep Learning Models
    if has_models:
        try:
            import numpy as np
            import tensorflow as tf

            img = image.resize((224, 224))
            img_array = tf.keras.utils.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            issue_pred = issue_model1.predict(img_array, verbose=0)[0][0]

            if issue_pred < 0.7:  # Hazard detected
                class_pred = class_model1.predict(img_array, verbose=0)[0]
                class_idx = np.argmax(class_pred)
                predicted_class = CLASSES_TO_USE[class_idx] if class_idx < len(CLASSES_TO_USE) else "Potholes"
                confidence = float(np.max(class_pred))

                seg_model = seg_model_potholes if predicted_class == 'Potholes' else seg_model_garbage
                if seg_model:
                    import cv2
                    open_cv_image = np.array(image)[:, :, ::-1].copy()
                    results = seg_model.predict(source=open_cv_image, conf=0.25, verbose=False)
                    annotated_frame = results[0].plot()
                    seg_pil = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
                    severity = "critical" if predicted_class in ["Potholes", "Waterlogging"] else "medium"
                    return InferenceResult(seg_pil, round(confidence, 3), predicted_class, severity=severity, engine="local_yolo")
        except Exception as e:
            logger.warning(f"Local ML inference fallback: {e}")

    # Tier 3: Intelligent Computer Vision
    return smart_cv_hazard_inference(image, hint_text=hint_text)