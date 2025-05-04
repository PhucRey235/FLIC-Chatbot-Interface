import streamlit as st
import time
import threading
from langchain_core.messages import AIMessage, HumanMessage
import queue
import streamlit_autorefresh

from .info_controller import save_tat_yeu_cau_nhan_vien

IDLE_TIMEOUT_SECONDS = 300
RERUN_TIME = 5

def clear_on_snapshot_state():
    if 'listener' in st.session_state:
        try:
            st.session_state.listener.unsubscribe()
        except Exception:
            pass
        del st.session_state.listener

    for var in ['message_queue', 'last_interaction_time', 'last_total_msg_count']:
        if var in st.session_state:
            del st.session_state[var]

    st.session_state.gap_nhan_vien = False
    try:
        save_tat_yeu_cau_nhan_vien()
    except Exception:
        pass

def reset_interact_interface():
    st.session_state.last_interaction_time = time.time()

def on_snapshot_callback_factory(q_ref):
    message_queue_ref = q_ref

    def on_snapshot_callback(doc_snapshot, changes, read_time):
        try:
            if not doc_snapshot:
                return

            for doc in doc_snapshot:
                if doc.exists:
                    data = doc.to_dict()
                    messages = data.get('messages', [])
                    queue_item = {"type": "data_update", "messages": messages}

                    try:
                        message_queue_ref.put_nowait(queue_item)
                    except queue.Full:
                        pass
                    except Exception:
                        pass
        except Exception:
            pass

    return on_snapshot_callback

def start_chat_monitoring():
    if 'message_queue' not in st.session_state:
        st.session_state.message_queue = queue.Queue()

    if 'listener' not in st.session_state:
        st.session_state.listener = None

    if 'last_interaction_time' not in st.session_state:
        st.session_state.last_interaction_time = time.time()

    if 'last_total_msg_count' not in st.session_state:
        st.session_state.last_total_msg_count = 0

    if st.session_state.get('listener') is None:
        doc_ref = st.session_state.firebase_db.collection("chatContent").document(
            st.session_state.get('id_session_dict', {}).get('conversationID', '')
        )
        message_queue_ref = st.session_state.message_queue
        firestore_callback = on_snapshot_callback_factory(message_queue_ref)
        listener_obj = doc_ref.on_snapshot(firestore_callback)
        st.session_state.listener = listener_obj
        reset_interact_interface()

    streamlit_autorefresh.st_autorefresh(
        interval=RERUN_TIME * 1000,
        limit=None,
        key="chat_monitor_auto_refresher"
    )

    if time.time() - st.session_state.get("last_interaction_time", time.time()) > IDLE_TIMEOUT_SECONDS:
        clear_on_snapshot_state()
        st.rerun()

def process_queue_and_update_state():
    while not st.session_state.message_queue.empty():
        try:
            item = st.session_state.message_queue.get_nowait()
            item_type = item.get("type", "unknown")

            if item_type == "data_update":
                new_messages = item.get("messages", [])
                processed = []

                if st.session_state.last_total_msg_count < len(new_messages):
                    for msg_data in new_messages:
                        content = msg_data.get('content', '')
                        text = content.get('text', str(content)) if isinstance(content, dict) else str(content)

                        sender = msg_data.get('sender', {})
                        sender_type = sender.get('type', '').lower() if isinstance(sender, dict) else str(sender).lower()

                        if sender_type == 'user':
                            processed.append(HumanMessage(content=text))
                        else:
                            processed.append(AIMessage(content=text))

                    st.session_state.last_total_msg_count = len(new_messages)
                    st.session_state.agent_history = processed
                    reset_interact_interface()

        except queue.Empty:
            break
