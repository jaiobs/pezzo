from flask import Flask, request, jsonify
from services.prompt_service import PromptService
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

@app.route('/api/prompts/v2/deployment', methods=['GET'])
def get_prompt():
    name = request.args.get('name')
    environment = request.args.get('environmentName')
    project_id = request.args.get('projectId')
    
    api_key = request.headers.get('x-pezzo-api-key')
    header_project_id = request.headers.get('x-pezzo-project-id')
    
    if not all([name, environment, project_id, api_key, header_project_id]):
        return jsonify({'message': 'Missing required parameters or headers', 'statusCode': 400}), 400

    if project_id != header_project_id:
        return jsonify({'message': 'Project ID mismatch between query parameters and headers', 'statusCode': 400}), 400

    try:
        result = PromptService.get_prompt_version(name, project_id, environment, api_key)
        
        if result is None:
            return jsonify({'message': 'Prompt version not found', 'statusCode': 404}), 404
            
        response_data = {
            "promptId": result.get("promptId"),
            "promptVersionSha": result.get("promptVersionSha"),
            "type": "Prompt", 
            "settings": {}, 
            "content": result.get("content")
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        if str(e) == "Invalid API key":
            return jsonify({'message': 'Unauthorized: Invalid API key', 'statusCode': 401}), 401
        return jsonify({'message': str(e), 'statusCode': 500}), 500

if __name__ == '__main__':
    if app.config.get('DEBUG', False):
        app.run(debug=True)
    else:
        http_server = WSGIServer(('0.0.0.0', 5000), app)
        print('Starting server on http://0.0.0.0:5000')
        http_server.serve_forever()