from flask import jsonify

def response(message, status="ok", code="ok", data={}):
  return jsonify({
    "status": "error" if code != "ok" else status,
    "code": code,
    "message": message,
    "data": data,
  })
