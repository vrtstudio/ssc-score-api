from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import requests
import re

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def calculate_score():
    data = request.get_json()
    pdf_url = data.get("pdf_url")
    user_answers = data.get("user_answers")

    if not pdf_url or not user_answers:
        return jsonify({"error": "Missing input"}), 400

    # Download PDF
    response = requests.get(pdf_url)
    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    # Extract text from PDF
    doc = fitz.open("temp.pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Extract correct answers from PDF using pattern
    correct_answers = re.findall(r"Q\d+\.\s+([A-D])", text)

    correct = incorrect = unattempted = 0
    for i, user in enumerate(user_answers.strip().upper()):
        if i >= len(correct_answers):
            break
        correct_ans = correct_answers[i]
        if user == correct_ans:
            correct += 1
        elif user == "_":
            unattempted += 1
        else:
            incorrect += 1

    total_score = correct * 2 - incorrect * 0.5

    return jsonify({
        "correct": correct,
        "incorrect": incorrect,
        "unattempted": unattempted,
        "total_score": total_score
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
