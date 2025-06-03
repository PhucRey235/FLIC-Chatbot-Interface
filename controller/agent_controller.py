import streamlit as st
import pathlib
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk, ToolMessage  # Định dạng tin nhắn

from model.tools import get_agent_for_sinh_vien, get_agent_for_hoc_vien  # Khởi tạo agent

from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from json_repair import repair_json
from pydantic import BaseModel, Field
import json
import time 
import re

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def init_llm_model():
    llm_model = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",  # Model Gemini
        temperature=0,  # Độ sáng tạo (0-1)
        max_tokens=10000,  # Số token tối đa trong phản hồi
        timeout=10,  # Thời gian chờ tối đa
        max_retries=2,  # Số lần thử lại nếu lỗi
        api_key=GOOGLE_API_KEY,
        safety_settings={  # Cấu hình chặn nội dung không phù hợp
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
    )
    
    return llm_model

class ResponseLLM(BaseModel):
    cau_tra_loi: str = Field(default="")
    su_dung_tool: str = Field(default="")
    noi_dung_truy_van_tool: str = Field(default="")
    tu_choi: int = Field(default=0)

def extract_json_from_markdown(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()

def process_llm_output(output_string: str):
    try:
        repaired_json_string = extract_json_from_markdown(output_string)
        data_dict = json.loads(repaired_json_string)
        validated_data = ResponseLLM(**data_dict)
        return validated_data.model_dump()
    except Exception as e:
        print(f"Lỗi khi sửa JSON hoặc xác thực Pydantic: {e}")
        # Trả về toàn bộ nội dung làm câu trả lời, các trường còn lại mặc định
        return ResponseLLM(cau_tra_loi=output_string.strip()).model_dump()

def get_answer(recent_history):
    if st.session_state.get('user_info', {}).get('la_hoc_vien', False) or st.session_state.get('user_info', {}).get('la_quan_ly', False):
        if "agent_executor_route" not in st.session_state:
            st.session_state.agent_executor_route, st.session_state.agent_executor_RAG, st.session_state.agent_executor_SQL = get_agent_for_hoc_vien()
            st.session_state.system_prompt_hoc_vien_route = pathlib.Path("model/prompts/system_prompt_hoc_vien_route.md").read_text(encoding='utf-8')

            st.session_state.system_prompt_hoc_vien_RAG = pathlib.Path("model/prompts/system_prompt_hoc_vien_RAG.md").read_text(encoding='utf-8')
            
            if st.session_state.get('user_info', {}).get('la_hoc_vien', False):
                system_prompt_hoc_vien_SQL = pathlib.Path("model/prompts/system_prompt_hoc_vien_SQL.md").read_text(encoding='utf-8')
                system_prompt_hoc_vien_SQL = system_prompt_hoc_vien_SQL.replace("{so_dien_thoai}", st.session_state.get('user_info', {}).get('phone', ''))
                st.session_state.system_prompt_SQL = system_prompt_hoc_vien_SQL.replace("{thoi_gian_hien_tai}", datetime.now().strftime("%d/%m/%Y %H:%M"))
        
            elif  st.session_state.get('user_info', {}).get('la_quan_ly', False):
                system_prompt_quan_ly_SQL = pathlib.Path("model/prompts/system_prompt_quan_ly_SQL.md").read_text(encoding='utf-8')
                system_prompt_quan_ly_SQL = system_prompt_quan_ly_SQL.replace("{so_dien_thoai}", st.session_state.get('user_info', {}).get('phone', ''))
                st.session_state.system_prompt_SQL = system_prompt_quan_ly_SQL.replace("{thoi_gian_hien_tai}", datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        
        system_prompt_hoc_vien_route = pathlib.Path("model/prompts/system_prompt_hoc_vien_route.md").read_text(encoding='utf-8')
        summarized_message = [SystemMessage(content=system_prompt_hoc_vien_route)]
        summarized_message.extend(recent_history) 
        
        output = st.session_state.agent_executor_route.invoke({"messages": summarized_message})    
        response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
        response_usage = output["messages"][-1].usage_metadata
        
        json_response = process_llm_output(response)

        if json_response["cau_tra_loi"]:
            return json_response["cau_tra_loi"], response_usage
        
        else:        
            if json_response['tu_choi'] == 1:
                return "Xin lỗi, tôi không thể thực thi yêu cầu đó.", response_usage
            
            elif json_response['tu_choi'] == 2:
                return "Hiện tại, chức năng tra cứu thông tin cá nhân cho khóa học TOEIC chưa được hỗ trợ trực tuyến.", response_usage
            
            elif json_response['tu_choi'] == 3:
                return "Hiện tại trung tâm chỉ tổ chức thi TOEIC phối hợp với IIG. Nếu bạn quan tâm luyện thi TOEIC, chúng tôi sẵn sàng hỗ trợ.", response_usage

            if json_response['su_dung_tool'] == 'RAG':
                noi_dung_truy_van_tool = json_response['noi_dung_truy_van_tool']
                st.write(noi_dung_truy_van_tool)
                summarized_message = [SystemMessage(content=st.session_state.system_prompt_hoc_vien_RAG)]
                summarized_message.append(HumanMessage(content=noi_dung_truy_van_tool)) 
                
                output = st.session_state.agent_executor_RAG.invoke({"messages": summarized_message}) 
                   
                response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
                response_usage = output["messages"][-1].usage_metadata
                
                return response, response_usage
                
            if json_response['su_dung_tool'] == 'SQL':
                noi_dung_truy_van_tool = json_response['noi_dung_truy_van_tool']
                
                summarized_message = [SystemMessage(content=st.session_state.system_prompt_SQL)]
                summarized_message.append(HumanMessage(content=noi_dung_truy_van_tool)) 
                
                output = st.session_state.agent_executor_SQL.invoke({"messages": summarized_message})    
                
                st.write(output)

                response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
                response_usage = output["messages"][-1].usage_metadata
                            
                st.write(response)
                time.sleep(100)
                              
                return response, response_usage
                         
    # Khởi tạo agent nếu chưa có
    elif not st.session_state.get('user_info', {}).get('la_hoc_vien', True):
        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = get_agent_for_sinh_vien()
            system_prompt_sinh_vien_RAG = pathlib.Path("model/prompts/system_prompt_sinh_vien_RAG.md").read_text(encoding='utf-8')
        
            st.session_state.system_prompt_sinh_vien_RAG = system_prompt_sinh_vien_RAG.replace("{thoi_gian_hien_tai}", datetime.now().strftime("%d/%m/%Y %H:%M"))
            
        summarized_message = [SystemMessage(content=st.session_state.system_prompt_sinh_vien_RAG)]
        summarized_message.extend(recent_history)    

        output = st.session_state.agent_executor.invoke({"messages": summarized_message})
        
        response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
        response_usage = output["messages"][-1].usage_metadata
        
        return response, response_usage
                
                
                
                
                