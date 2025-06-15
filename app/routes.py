import os
from app import app
from flask import render_template
from flask import request
from app.controllers.ChatController import ChatController
from app.controllers.KnowledgeSummaryController import KnowledgeSummaryController
from app.utils.markdown_helper import render_markdown
from app.memory.session_registry import init_session_table, add_session
from flask import jsonify


@app.route('/')
def home():
    return render_template('views/home.html')

@app.route('/chat')
def chat():
    init_session_table()  
    topic = request.args.get('topic')
    mode = request.args.get('mode')
    session_id =add_session(topic, mode) 
    return render_template('views/chat.html', topic=topic, mode=mode,session_id=session_id)

@app.route('/summary', methods=['POST'])
def summary():
    topic = request.form.get('topic')
    mode = request.form.get('mode')
    print(f"[INFO] Ringkasan untuk topik: {topic}, mode: {mode}, file: ")
    markdown=KnowledgeSummaryController().summarize( topic)
    summary = render_markdown(markdown)
    return render_template('views/summary.html', topic=topic, mode=mode ,summary=summary, markdown=markdown)

@app.route('/api/chat', methods=['POST'])
def chat_route():
    data = request.get_json()
    input = data.get('message')
    topic = data.get('topic')
    mode = request.args.get('mode')
    controller = ChatController() 
    if mode == 'learn':
        return controller.chat_learn(input,topic)
    elif mode == 'daily':
        return controller.chat_daily(input, topic)
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
    
# @app.route("/api/clear_memory", methods=["GET"])
# def clear_route():
#     return MemoryManager().clear_memory()