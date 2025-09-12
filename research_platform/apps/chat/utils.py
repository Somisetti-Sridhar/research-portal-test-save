# import os
# import string
# import logging
# import joblib
# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.sequence import pad_sequences
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
# from django.conf import settings

# # ----------------------------
# # Suppress TF logs
# # ----------------------------
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# logging.getLogger("tensorflow").setLevel(logging.ERROR)

# # ----------------------------
# # Paths (relative for Django deployment)
# # ----------------------------
# USE_ABS_PATH = True  
# if USE_ABS_PATH:
#     MODEL_PATH = r"D:\bbb\research_platform\apps\ml_engine\ml_models\hate_speech_detection.keras"
#     TOKENIZER_PATH = r"D:\bbb\research_platform\apps\ml_engine\ml_models\tokenizer.pkl"
# else:
#     MODEL_PATH = os.path.join(
#         settings.BASE_DIR, "apps", "ml_engine", "ml_models", "hate_speech_detection.keras"
#     )
#     TOKENIZER_PATH = os.path.join(
#         settings.BASE_DIR, "apps", "ml_engine", "ml_models", "tokenizer.pkl"
#     )

# # ----------------------------
# # Constants
# # ----------------------------
# MAX_LEN = 50  # must match training
# ESSENTIAL_WORDS = {"i", "you", "love", "hate", "not", "no", "please", "thanks"}
# stop_words = set(stopwords.words("english")) - ESSENTIAL_WORDS
# lemmatizer = WordNetLemmatizer()

# CLASS_MAPPING = {0: "hate", 1: "offensive", 2: "neutral"}
# OFFENSIVE_CLASSES = {"hate", "offensive"}

# # ----------------------------
# # Globals for lazy caching
# # ----------------------------
# _hate_model = None
# _tokenizer = None


# def _load_once():
#     """Lazy-load model + tokenizer only once per worker."""
#     global _hate_model, _tokenizer

#     if _hate_model is None:
#         if not os.path.exists(MODEL_PATH):
#             raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
#         _hate_model = load_model(MODEL_PATH)

#     if _tokenizer is None:
#         if not os.path.exists(TOKENIZER_PATH):
#             raise FileNotFoundError(f"Tokenizer not found at {TOKENIZER_PATH}")
#         _tokenizer = joblib.load(TOKENIZER_PATH)


# def get_hate_model():
#     global _hate_model
#     if _hate_model is None:
#         _load_once()
#     return _hate_model


# def get_tokenizer():
#     global _tokenizer
#     if _tokenizer is None:
#         _load_once()
#     return _tokenizer


# # ----------------------------
# # Text preprocessing
# # ----------------------------
# def clean_text(text: str) -> str:
#     text = str(text).lower()
#     text = text.translate(str.maketrans("", "", string.punctuation))
#     words = [
#         lemmatizer.lemmatize(word)
#         for word in text.split()
#         if word not in stop_words
#     ]
#     return " ".join(words)


# # ----------------------------
# # Prediction
# # ----------------------------
# def predict_classes(messages: list[str], confidence_threshold: float = 0.0) -> list[str]:
#     if not messages:
#         return []

#     texts = [clean_text(m) for m in messages]
#     seqs = get_tokenizer().texts_to_sequences(texts)
#     seqs = [[0] if not s else s for s in seqs]  # fallback for empty seqs

#     padded = pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")
#     preds = get_hate_model().predict(padded, verbose=0)

#     results = []
#     for p in preds:
#         cls_idx = int(np.argmax(p))
#         cls_prob = float(np.max(p))
#         if cls_prob < confidence_threshold:
#             results.append("uncertain")
#         else:
#             results.append(CLASS_MAPPING[cls_idx])
#     return results


# def predict_class(message: str, confidence_threshold: float = 0.0) -> str:
#     return predict_classes([message], confidence_threshold=confidence_threshold)[0]


# def is_offensive(message: str, confidence_threshold: float = 0.0) -> bool:
#     cls = predict_class(message, confidence_threshold=confidence_threshold)
#     return cls in OFFENSIVE_CLASSES


# def are_offensive(messages: list[str], confidence_threshold: float = 0.0) -> list[bool]:
#     classes = predict_classes(messages, confidence_threshold=confidence_threshold)
#     return [cls in OFFENSIVE_CLASSES for cls in classes]


# # ----------------------------
# # Optional: warmup (call once at startup)
# # ----------------------------
# def warmup():
#     """Preload model + tokenizer into memory at startup (optional)."""
#     _load_once()


# # ----------------------------
# # Example usage
# # ----------------------------
# if __name__ == "__main__":
#     # Uncomment this if you want to warmup manually
#     # warmup()

#     test_texts = [
#         "fuck you",
#         "I love you",
#         "you are amazing",
#         "please help me",
#         "random unknown words",
#     ]
#     preds = predict_classes(test_texts, confidence_threshold=0.5)
#     blocked = are_offensive(test_texts, confidence_threshold=0.5)

#     for t, p, b in zip(test_texts, preds, blocked):
#         print(f"Text: {t} --> Prediction: {p} | Blocked: {b}")
def is_offensive(message):
    return False