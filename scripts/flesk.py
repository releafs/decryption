from flask import Flask, request, jsonify, abort
import hmac
import hashlib
import os

app = Flask(__name__)

# GitHub Secret for signature validation
SECRET = os.getenv('GITHUB_SECRET')

# Function to validate GitHub signature
def validate_github_signature(payload_body, signature):
    mac = hmac.new(SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate GitHub signature
    signature = request.headers.get('X-Hub-Signature-256')
    payload_body = request.get_data()

    if not validate_github_signature(payload_body, signature):
        abort(403)  # Invalid signature

    # Handle the workflow event
    payload = request.json
    if payload.get('action') == 'completed':
        workflow_status = payload.get('workflow_run', {}).get('conclusion')
        if workflow_status == 'success':
            # Handle successful workflow
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'failed'})
    return '', 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
