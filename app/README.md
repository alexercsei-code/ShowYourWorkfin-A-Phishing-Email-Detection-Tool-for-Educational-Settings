# Show Your Workfin – app

Streamlit interface for the phishing checker.

    pip install -r ../requirements.txt
    streamlit run app.py

`model/` holds the trained model (`phishing_model.joblib`), the feature code it depends on (`features.py`)
and `model_info.txt`. The app scores the email body with the model and, if the full message source is
pasted, reports SPF / DKIM / DMARC results from the `Authentication-Results` header. Nothing pasted is stored.
Warning bands: below 30% "probably legitimate", 30–70% "be cautious", 70% and above "likely phishing".