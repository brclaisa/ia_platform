import os

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Assistente IA MultiAgente",
    page_icon="🤖",
    layout="wide",
)


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("metadata"):
                meta = msg["metadata"]
                cols = st.columns(3)
                with cols[0]:
                    compliance = "Aprovado" if meta.get("is_compliant") else "Bloqueado"
                    st.caption(f"Compliance: {compliance}")
                with cols[1]:
                    if meta.get("route"):
                        st.caption(f"Rota: {meta['route'].upper()}")
                with cols[2]:
                    if meta.get("sources"):
                        st.caption(f"Fontes: {', '.join(meta['sources'])}")


def send_question(question: str):
    try:
        with httpx.Client(timeout=120) as client:
            response = client.post(f"{API_URL}/ask", json={"question": question})
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {"error": "Não foi possível conectar à API. Verifique se o servidor está rodando."}
    except httpx.HTTPStatusError as e:
        return {"error": f"Erro da API: {e.response.status_code}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}


def upload_document(file):
    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{API_URL}/documents",
                files={"file": (file.name, file.getvalue(), file.type or "application/octet-stream")},
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {"error": "Não foi possível conectar à API."}
    except Exception as e:
        return {"error": f"Erro: {e}"}


with st.sidebar:
    st.title("Documentos")
    st.markdown("Faça upload de documentos para a base de conhecimento.")

    uploaded_file = st.file_uploader(
        "Selecione um arquivo",
        type=["txt", "md", "pdf"],
        help="Formatos suportados: TXT, MD, PDF",
    )

    if uploaded_file and st.button("Processar documento", type="primary"):
        with st.spinner("Processando..."):
            result = upload_document(uploaded_file)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(
                    f"**{result['filename']}** processado!\n\n"
                    f"Chunks criados: {result['chunks_created']}"
                )

    st.divider()
    st.markdown(
        "**Como funciona:**\n"
        "1. Sua pergunta passa por verificação de compliance\n"
        "2. O sistema decide se usa documentos (RAG) ou responde diretamente\n"
        "3. A resposta é formatada e entregue"
    )

st.title("Assistente IA MultiAgente")
st.caption("Assistente inteligente com compliance, RAG e agentes especializados")

init_session()
display_chat_history()

if question := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            result = send_question(question)

        if "error" in result:
            st.error(result["error"])
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Erro: {result['error']}"}
            )
        else:
            st.markdown(result["answer"])
            metadata = {
                "is_compliant": result.get("is_compliant"),
                "route": result.get("route"),
                "sources": result.get("sources", []),
            }
            cols = st.columns(3)
            with cols[0]:
                compliance = "Aprovado" if result.get("is_compliant") else "Bloqueado"
                st.caption(f"Compliance: {compliance}")
            with cols[1]:
                if result.get("route"):
                    st.caption(f"Rota: {result['route'].upper()}")
            with cols[2]:
                if result.get("sources"):
                    st.caption(f"Fontes: {', '.join(result['sources'])}")

            st.session_state.messages.append(
                {"role": "assistant", "content": result["answer"], "metadata": metadata}
            )
