/**
 * Offline AI Manager.
 * Runs a lightweight on-device model (TensorFlow.js) when connectivity is poor.
 * Expected env vars: None
 * Testing tips: Mock tf.loadLayersModel and ensure predictions are cached.
 */
import { saveOfflineScan } from './offline_storage';

let modelPromise: Promise<any> | null = null;

async function loadModel() {
  if (!modelPromise) {
    // Dynamically import TensorFlow.js only when needed.
    modelPromise = import('@tensorflow/tfjs')
      .then(async (tf) => {
        const m = await tf.loadLayersModel('/models/offline_disease_model.json');
        return { tf, model: m };
      })
      .catch(() => null);
  }
  return modelPromise;
}

export async function runOfflineScan(
  imageElement: HTMLVideoElement | HTMLImageElement,
  geo: { lat: number; lon: number } | null,
) {
  const loaded = await loadModel();
  if (!loaded) {
    return null;
  }
  const { tf, model } = loaded;

  const tensor = tf.tidy(() =>
    tf.browser
      .fromPixels(imageElement)
      .resizeBilinear([224, 224])
      .toFloat()
      .div(255)
      .expandDims(0),
  );
  const logits = (model.predict(tensor) as any) as { data: () => Promise<Float32Array> };
  const scores = await logits.data();
  tf.dispose([tensor, logits]);

  let bestIdx = 0;
  let bestScore = scores[0] ?? 0;
  for (let i = 1; i < scores.length; i += 1) {
    if (scores[i] > bestScore) {
      bestScore = scores[i];
      bestIdx = i;
    }
  }

  const diseaseLabels = [
    'Healthy',
    'Early blight',
    'Late blight',
    'Powdery mildew',
    'Rust',
    'Leaf spot',
  ];
  const label = diseaseLabels[bestIdx] ?? 'Unknown';

  const dataUrlCanvas = document.createElement('canvas');
  dataUrlCanvas.width = imageElement.clientWidth || 224;
  dataUrlCanvas.height = imageElement.clientHeight || 224;
  const ctx = dataUrlCanvas.getContext('2d');
  if (ctx && imageElement instanceof HTMLVideoElement) {
    ctx.drawImage(imageElement, 0, 0, dataUrlCanvas.width, dataUrlCanvas.height);
  }
  const scan_image = dataUrlCanvas.toDataURL('image/jpeg', 0.7);

  await saveOfflineScan({
    scan_image,
    local_prediction: label,
    timestamp: new Date().toISOString(),
    geo_location: geo,
  });

  return { label, confidence: bestScore };
}

