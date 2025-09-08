from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil
import zipfile
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 文件存储路径
FILE_STORAGE_PATH = '/root/project/zen_example/frontend/data'

# 确保存储目录存在
os.makedirs(FILE_STORAGE_PATH, exist_ok=True)

@app.route('/api/files', methods=['GET'])
def list_files():
    """获取文件列表"""
    try:
        path = request.args.get('path', '')
        full_path = os.path.join(FILE_STORAGE_PATH, path) if path else FILE_STORAGE_PATH
        
        if not os.path.exists(full_path):
            return jsonify({'error': '路径不存在'}), 404
            
        files = []
        
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            relative_path = os.path.join(path, item) if path else item
            
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    'name': item,
                    'type': 'file',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': relative_path
                })
            elif os.path.isdir(item_path):
                stat = os.stat(item_path)
                files.append({
                    'name': item,
                    'type': 'folder',
                    'size': 0,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': relative_path
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        path = request.form.get('path', '')
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        filename = secure_filename(file.filename)
        upload_path = os.path.join(FILE_STORAGE_PATH, path) if path else FILE_STORAGE_PATH
        
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        
        file.save(file_path)
        
        return jsonify({'message': '文件上传成功', 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/folder', methods=['POST'])
def create_folder():
    """创建文件夹"""
    try:
        data = request.get_json()
        folder_name = data.get('name')
        path = data.get('path', '')
        
        if not folder_name:
            return jsonify({'error': '文件夹名称不能为空'}), 400
            
        folder_name = secure_filename(folder_name)
        base_path = os.path.join(FILE_STORAGE_PATH, path) if path else FILE_STORAGE_PATH
        folder_path = os.path.join(base_path, folder_name)
        
        if os.path.exists(folder_path):
            return jsonify({'error': '文件夹已存在'}), 400
            
        os.makedirs(folder_path)
        
        return jsonify({'message': '文件夹创建成功', 'name': folder_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    try:
        file_path = os.path.join(FILE_STORAGE_PATH, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
            
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            # 如果是文件夹，创建zip文件
            zip_filename = f"{os.path.basename(filename)}.zip"
            zip_path = f"/tmp/{zip_filename}"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        file_path_in_zip = os.path.join(root, file)
                        arcname = os.path.relpath(file_path_in_zip, file_path)
                        zipf.write(file_path_in_zip, arcname)
            
            return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete', methods=['DELETE'])
def delete_item():
    """删除文件或文件夹"""
    try:
        data = request.get_json()
        item_path = data.get('path')
        
        if not item_path:
            return jsonify({'error': '路径不能为空'}), 400
            
        full_path = os.path.join(FILE_STORAGE_PATH, item_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': '文件或文件夹不存在'}), 404
            
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            shutil.rmtree(full_path)
            
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)