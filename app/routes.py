import os
from app import app
from flask import render_template
from flask import request
from pprint import pprint
from app.controllers.ChatController import ChatController
from app.controllers.KnowledgeSummaryController import KnowledgeSummaryController
from app.models.memory_model import MemoryManager
from app.utils.markdown_helper import render_markdown
from datetime import datetime
from flask import jsonify


@app.route('/')
def home():
    return render_template('views/home.html')
@app.route('/chat')
def chat():
    topic = request.args.get('topic')
    mode = request.args.get('mode')
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"short_memory_{date_str}_{topic}_{mode}.json"
    return render_template('views/chat.html', topic=topic, mode=mode, filename=filename)
@app.route('/summary', methods=['POST'])
def summary():
    topic = request.form.get('topic')
    mode = request.form.get('mode')
    short_memory_filename = request.form.get('filename')
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[INFO] Ringkasan untuk topik: {topic}, mode: {mode}, file: {short_memory_filename}")
    markdown=KnowledgeSummaryController().summarize(short_memory_filename, topic)
    filename = f"summary_{date_str}_{topic}_{mode}.json"
    summary = render_markdown(markdown)
    return render_template('views/summary.html', topic=topic, mode=mode, filename=filename ,summary=summary, markdown=markdown)
@app.route('/api/chat', methods=['POST'])
def chat_route():
    data = request.get_json()
    input = data.get('message')
    filename = data.get('filename')
    topic = data.get('topic')
    mode = request.args.get('mode')
    controller = ChatController() 
    if mode == 'learn':
        return controller.chat_learn(input, filename,topic)
    elif mode == 'daily':
        return controller.chat_daily(input, filename, topic)
    else:
        return 'silahkan pilih mode chat yang benar', 400

@app.route('/api/summary/summary', methods=['POST'])
def summary_route():
    data = request.get_json()
    input = data.get('message')
    summary = KnowledgeSummaryController.summarize(input)
    return render_template('summary_result.html', summary=summary)

@app.route('/api/summary/revise', methods=['POST'])
def revise_route():
    data = request.get_json()
    current_summary = data.get('current_summary')
    user_feedback = data.get('user_feedback')
    topic = data.get('topic')
    
    controller = KnowledgeSummaryController()
    return controller.process_revision(current_summary, user_feedback, topic)

@app.route('/api/summary/remember', methods=['POST'])
def remember_route():
    summary = request.data.decode('utf-8')
    controller = KnowledgeSummaryController()
    result = controller.create_new_memories(summary)
    return jsonify(result)
    
@app.route("/api/clear_memory", methods=["GET"])
def clear_route():
    return MemoryManager().clear_memory()