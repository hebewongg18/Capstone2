from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import os, tempfile, cv2, uuid

app = Flask(__name__)
CORS(app)

model = YOLO("best.pt")
os.makedirs("static/results", exist_ok=True)

@app.route("/")
def home():
    return "YOLOv8 backend is running!"

@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    suffix = os.path.splitext(file.filename)[-1].lower()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    file.save(temp_file.name)

    try:
        if suffix in [".jpg", ".jpeg", ".png"]:
            results = model(temp_file.name)
            predictions = []
            if results[0].boxes is not None:
                for pred in results[0].boxes:
                    cls = int(pred.cls[0])
                    predictions.append(results[0].names[cls])
            result_frame = results[0].plot()
            image_result_path = os.path.join("static/results", f"{uuid.uuid4().hex}.jpg")
            cv2.imwrite(image_result_path, result_frame)
            return jsonify({
                "detections": predictions,
                "image_url": f"/{image_result_path}",
                "type": "image"
            })

        elif suffix in [".mp4", ".mov", ".avi", ".mkv"]:
            video_output_path, predictions = detect_video_and_save(temp_file.name)
            filename = os.path.basename(video_output_path)
            return jsonify({
                "detections": predictions,
                "video_url": f"/static/results/{filename}",
                "type": "video"
            })

        else:
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            os.unlink(temp_file.name)
        except Exception:
            pass

def detect_video_and_save(file_path):
    cap = cv2.VideoCapture(file_path)
    filename = f"{uuid.uuid4().hex}_out.mp4"
    output_path = os.path.join("static/results", filename)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    detections = set()
    frame_count = 0
    skip_frame = 10

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % skip_frame != 0:
            out.write(frame)
            continue

        results = model.predict(source=frame, show=False, conf=0.25, verbose=False, imgsz=512)
        if results[0].boxes is not None:
            for pred in results[0].boxes:
                cls = int(pred.cls[0])
                detections.add(results[0].names[cls])
        result_frame = results[0].plot()
        out.write(result_frame)

    cap.release()
    out.release()
    return output_path, list(detections)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
