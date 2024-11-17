from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
data = ["fucking hate you"]
sentiment_label = sentiment_pipeline(data)[0]
if sentiment_label["label"] == "NEGATIVE":
    score = -1*sentiment_label["score"]
else:
    score = sentiment_label["score"]
print(score)