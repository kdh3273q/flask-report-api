from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pyautogui, pyperclip, time, os
import subprocess, threading, uuid

app = Flask(__name__)
CORS(app)
jobs = {}  # job_id → {"status": "running", "result": "..."}

def run_command_async(job_id, cmd):
    try:
        print(f"[{job_id}] 명령 실행 시작: {cmd}")
        result_file = f"result_{job_id}.txt"
        redirected_cmd = f"{cmd} > {result_file} 2>&1"

        # 1. Cursor IDE에 원본 명령어만 입력
        #pyautogui.hotkey('command', 'k')
        #time.sleep(0.6)

        pyperclip.copy(cmd)
        pyautogui.hotkey('command', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')

        print(f"[{job_id}] Cursor IDE에 명령 입력 완료")

        result_file = f"result_{job_id}.txt"
        redirected_cmd = f"{cmd} > {result_file} 2>&1"
        project_dir = "/Users/Mac/Downloads/cursor"  # 꼭 바꿔줘!

        # 실제 명령 실행
        subprocess.run(redirected_cmd, shell=True, cwd=project_dir)

        # 결과가 생성될 때까지 대기 (최대 60초)
        wait_time = 0
        max_wait = 60
        while not os.path.exists(os.path.join(project_dir, result_file)) and wait_time < max_wait:
            time.sleep(1)
            wait_time += 1
            print(f"[{job_id}] 결과 파일 대기 중... ({wait_time}s)")

        if not os.path.exists(os.path.join(project_dir, result_file)):
            raise Exception("결과 파일이 생성되지 않았습니다.")

        # 결과 읽기
        with open(os.path.join(project_dir, result_file), 'r', encoding='utf-8') as f:
            result_output = f.read()

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result_output
        print(f"[{job_id}] 결과 저장 완료 ✅")

        # 파일 삭제는 선택 사항
        #os.remove(os.path.join(project_dir, result_file))

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["result"] = str(e)
        print(f"[{job_id}] 실행 실패 ❌: {e}")

@app.route('/cursor', methods=['POST'])
def send_to_cursor():
    cmd = request.json.get('command', '')
    if not cmd:
        return jsonify({'error': 'no command'}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "result": None}

    threading.Thread(target=run_command_async, args=(job_id, cmd)).start()
    return jsonify({'status': 'started', 'job_id': job_id})

#@app.route('/result/<job_id>', methods=['GET'])
#def get_result(job_id):
#    job = jobs.get(job_id)
#    if not job:
#        return jsonify({'error': 'Job not found'}), 404
#    return jsonify(job)
#


@app.route('/result/<job_id>', methods=['GET'])
def download_excel(job_id):
    # 엑셀 파일 경로 (예: result_abc123.xlsx)
    file_path = f"/Users/Mac/Downloads/cursor/lcap_cursor_playwright/tests/excel_output/TEST_CSR250800000001_ai.xlsx"

    if not os.path.exists(file_path):
        return {"error": "File not found"}, 404

    return send_file(file_path, as_attachment=True, download_name=f"TEST_{job_id}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == '__main__':
    app.run(port=8080)
