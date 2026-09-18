/*
 * hand_capture.js
 *
 * Runs MediaPipe Hands in the browser, builds the same 126-value
 * feature vector used by real-time-isl-recognition (left(63) + right(63),
 * wrist-relative, scale-normalized by wrist-to-middle-MCP distance),
 * sends it to /recognition/predict/, and runs the same
 * IDLE -> CHARGING -> COMMITTED debounce logic as realtime_predict.py
 * so a sign has to be held steady before it counts as an answer.
 *
 * Expects a global `window.SIGNLEARN_TEST` object set by the test
 * template (attemptId, targetLetter, answerUrl, resultUrl, csrfToken,
 * predictUrl) and these elements in the page:
 *   #input-video     <video>
 *   #capture-canvas  hidden <canvas> used to mirror frames before MediaPipe
 *   #status-text     status messages
 *   #prediction-text live "Detected: X (NN%)" readout
 *   #target-letter   shows the letter the user should sign
 *   #score-text      running score
 */
(function () {
  const cfg = window.SIGNLEARN_TEST;
  if (!cfg) return;

  const NUM_LANDMARKS = 21;
  const FEATURES_PER_HAND = NUM_LANDMARKS * 3; // 63
  const TOTAL_FEATURES = FEATURES_PER_HAND * 2; // 126

  const CHARGE_BUFFER_SIZE = 10; // matches realtime_predict.py
  const CHARGE_THRESHOLD = 8;
  const CONFIDENCE_THRESHOLD = 0.7;
  const PREDICT_INTERVAL_MS = 150; // throttle calls to the backend

  const videoEl = document.getElementById("input-video");
  const captureCanvas = document.getElementById("capture-canvas");
  const captureCtx = captureCanvas.getContext("2d");
  const statusText = document.getElementById("status-text");
  const predictionText = document.getElementById("prediction-text");
  const targetLetterEl = document.getElementById("target-letter");
  const scoreText = document.getElementById("score-text");

  let chargeBuffer = [];
  let committedLabel = null;
  let lastPredictTime = 0;
  let busy = false;
  let locked = false; // true while submitting an answer / moving to next question

  // ------------------------------------------------------------------
  // Same math as normalize_single_hand() in extract_landmarks.py /
  // realtime_predict.py: subtract the wrist, divide by wrist-to-
  // middle-finger-MCP (landmark 9) distance.
  // ------------------------------------------------------------------
  function normalizeSingleHand(landmarks) {
    const wrist = landmarks[0];
    const coords = landmarks.map((lm) => [lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z]);

    const mid = coords[9];
    const scale = Math.sqrt(mid[0] * mid[0] + mid[1] * mid[1] + mid[2] * mid[2]);

    const out = [];
    for (const [x, y, z] of coords) {
      if (scale > 1e-6) {
        out.push(x / scale, y / scale, z / scale);
      } else {
        out.push(x, y, z);
      }
    }
    return out; // 63 values
  }

  // Same layout as landmarks_to_feature_vector(): left hand -> [0:63],
  // right hand -> [63:126], missing hand -> zeros.
  function buildFeatureVector(results) {
    let left = new Array(FEATURES_PER_HAND).fill(0);
    let right = new Array(FEATURES_PER_HAND).fill(0);

    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      return null;
    }

    results.multiHandLandmarks.forEach((landmarks, i) => {
      const handedness = results.multiHandedness[i];
      const label = handedness.label; // "Left" or "Right"
      const features = normalizeSingleHand(landmarks);
      if (label === "Left") {
        left = features;
      } else {
        right = features;
      }
    });

    return left.concat(right); // 126 values
  }

  async function callPredict(vector) {
    const resp = await fetch(cfg.predictUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": cfg.csrfToken,
      },
      body: JSON.stringify({ landmarks: vector }),
    });

    let data;
    try {
      data = await resp.json();
    } catch (e) {
      data = { error: "Server returned a non-JSON response (status " + resp.status + ")" };
    }

    if (!resp.ok && !data.error) {
      data.error = "Request failed with status " + resp.status;
    }

    return data;
  }

  async function submitAnswer(letter, confidence) {
    locked = true;
    statusText.textContent = "Recording answer\u2026";

    const resp = await fetch(cfg.answerUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": cfg.csrfToken,
      },
      body: JSON.stringify({ letter: letter, confidence: confidence }),
    });

    if (!resp.ok) {
      statusText.textContent = "Something went wrong recording your answer.";
      locked = false;
      return;
    }

    const data = await resp.json();
    if (scoreText) scoreText.textContent = data.score;

    if (data.finished) {
      statusText.textContent = "Test complete! Redirecting to results\u2026";
      setTimeout(() => {
        window.location.href = cfg.resultUrl;
      }, 800);
      return;
    }

    targetLetterEl.textContent = data.next_letter;
    predictionText.textContent = "";
    chargeBuffer = [];
    committedLabel = null;

    statusText.textContent = data.is_correct
      ? "Correct! Show the next sign."
      : "Not quite \u2014 show the next sign.";

    setTimeout(() => {
      locked = false;
    }, 600);
  }

  async function onResults(results) {
    if (locked) return;

    const now = performance.now();
    if (now - lastPredictTime < PREDICT_INTERVAL_MS || busy) return;

    const vector = buildFeatureVector(results);
    if (!vector) {
      statusText.textContent = "Show your hand to the camera.";
      chargeBuffer = [];
      committedLabel = null;
      return;
    }

    lastPredictTime = now;
    busy = true;
    const prediction = await callPredict(vector);
    busy = false;

    if (!prediction || prediction.error) {
      statusText.textContent = "Recognition error: " + (prediction && prediction.error ? prediction.error : "unknown");
      return;
    }

    const { letter, confidence } = prediction;
    predictionText.textContent = `Detected: ${letter} (${(confidence * 100).toFixed(0)}%)`;

    if (confidence < CONFIDENCE_THRESHOLD) {
      chargeBuffer = [];
      return;
    }

    chargeBuffer.push(letter);
    if (chargeBuffer.length > CHARGE_BUFFER_SIZE) chargeBuffer.shift();

    if (chargeBuffer.length === CHARGE_BUFFER_SIZE) {
      const counts = {};
      chargeBuffer.forEach((l) => (counts[l] = (counts[l] || 0) + 1));

      let best = null;
      let bestCount = 0;
      for (const [l, c] of Object.entries(counts)) {
        if (c > bestCount) {
          best = l;
          bestCount = c;
        }
      }

      if (bestCount >= CHARGE_THRESHOLD && best !== committedLabel) {
        committedLabel = best;
        statusText.textContent = `Locked in: ${best}`;
        submitAnswer(best, confidence);
      }
    }
  }

  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
  });

  hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.6,
    minTrackingConfidence: 0.6,
  });

  hands.onResults(onResults);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      videoEl.srcObject = stream;
      await videoEl.play();

      captureCanvas.width = videoEl.videoWidth || 640;
      captureCanvas.height = videoEl.videoHeight || 480;

      statusText.textContent = "Show the sign for " + cfg.targetLetter;

      const loop = async () => {
        // Mirror the frame horizontally before feeding MediaPipe, matching
        // the desktop recognizer's cv2.flip(frame, 1) so handedness
        // (left/right) stays consistent with how the model was trained.
        captureCtx.save();
        captureCtx.scale(-1, 1);
        captureCtx.drawImage(
          videoEl,
          -captureCanvas.width,
          0,
          captureCanvas.width,
          captureCanvas.height
        );
        captureCtx.restore();

        await hands.send({ image: captureCanvas });
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    } catch (err) {
      statusText.textContent = "Could not access the camera: " + err.message;
    }
  }

  startCamera();
})();
