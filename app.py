from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/result/<job_id>', methods=['GET'])
def download_excel(job_id):
    file_path = f"./results/result_{job_id}.xlsx"
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"테스트결과_{job_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))  # Render 환경에서 포트 받기
    app.run(host='0.0.0.0', port=port)
