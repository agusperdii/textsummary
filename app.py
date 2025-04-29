from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
# from summarizer import summarize, extract_keywords
from summ import summarize_texts
from pdf import create_pdf
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def get_summary():
    try:
        text = request.form['text']
        summary, keywords = summarize_texts(text)
        # keywords = extract_keywords(text)
        return jsonify({'summary': summary, 'keywords': ', '.join(keywords), 'text': text})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/result')
def result():
    summary = request.args.get('summary', '')
    keywords = request.args.get('keywords', '')
    text = request.args.get('text', '')  # ambil text
    return render_template('result.html', summary=summary, keywords=keywords, text=text)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        summary = request.form['summary']
        keywords = request.form['keywords']
        text = request.form['text']

        title = "Summary Report"
        cue_points = keywords.replace(',', '<br/>')
        notes = text
        summary_text = summary

        # Buat file PDF sementara
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        create_pdf(title, cue_points, notes, summary_text, temp.name)
        temp.close()

        # Kirim file ke user
        return send_file(temp.name, as_attachment=True, download_name="summary_report.pdf")
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
