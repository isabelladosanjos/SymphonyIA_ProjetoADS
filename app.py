# app.py

import streamlit as st
from groq import Groq

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Symphony IA",
    page_icon="🎵",
    layout="centered"
)

# --- CÓDIGO DE DESIGN (CSS) ---
def load_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            html, body, [class*="st-"], .stTextInput, .stTextArea, .stMarkdown {
                font-family: 'Inter', sans-serif;
            }
            h1 {
                color: #8e44ad;
                text-align: center;
                font-weight: 700;
            }
            .stWrite > p {
                text-align: center;
                font-size: 1.1rem;
            }
            [data-testid="stButton"] button {
                background-color: #8e44ad;
                color: white;
                border-radius: 12px;
                border: none;
                padding: 10px 24px;
                width: 100%;
                font-weight: 600;
                transition: background-color 0.3s ease;
            }
            [data-testid="stButton"] button:hover {
                background-color: #9b59b6;
                border: none;
                color: white;
            }
            [data-testid="stTextArea"] textarea:focus {
                 border-color: #9b59b6 !important;
                 box-shadow: 0 0 0 1px #9b59b6 !important;
            }
            h3 {
                color: #8e44ad;
                border-bottom: 2px solid #8e44ad;
                padding-bottom: 5px;
            }
            strong {
                color: #9b59b6;
                font-weight: 600;
            }
             .stSpinner > div > div {
                border-top-color: #8e44ad;
            }
            
            /* CSS para o expander foi removido */

        </style>
    """, unsafe_allow_html=True)

# Chama a função para carregar o CSS
load_css()

# --- Inicializa o Histórico de Playlists no Session State ---
if 'playlist_history' not in st.session_state:
    st.session_state.playlist_history = []


# --- 2. Configuração da Chave de API (lendo do secrets.toml) ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except Exception as e:
    st.error(f"Erro ao configurar a API Key do Groq: {e}")
    st.error("Verifique se você criou o arquivo .streamlit/secrets.toml e colocou sua GROQ_API_KEY.")
    st.stop() # Corrigido

# --- 3. Inicializa o Cliente Groq ---
client = Groq(api_key=API_KEY)

# --- 4. Definição do Modelo ---
MODEL_NAME = "llama-3.1-8b-instant"
model = "llama-3.1-8b-instant"

# --- 5. Prompt do Sistema ---
system_prompt = """
Você é o "Symphony Scout", um especialista em descobrir músicas que se conectam com a alma das pessoas.
Sua missão é ouvir o sentimento de um usuário e recomendar 3 músicas ou artistas pouco conhecidos que sejam a trilha sonora perfeita para aquele momento.

Para cada recomendação, forneça o nome do artista e da música, e explique em um parágrafo curto e poético por que aquela música se conecta com o que o usuário está sentindo.

Priorize artistas de indie, folk, acústico e gêneros mais calmos. Evite artistas mainstream.
A resposta deve ser formatada em Markdown, usando **negrito** para os nomes.
"""

# --- 6. Interface Gráfica ---
st.title("🎵 Symphony IA")
st.write("Me diga como você está se sentindo, o que está fazendo ou uma memória, e eu encontrarei a trilha sonora perfeita para o seu momento.")

user_input = st.text_area("Descreva seu sentimento ou momento aqui...", height=100, label_visibility="collapsed")

if st.button("Encontrar minha trilha sonora ✨"):
    if user_input:
        
        with st.spinner("Analisando seus sentimentos na velocidade da luz..."):
            try:
                # --- 7. A Chamada da API Groq ---
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7, 
                )
                
                ia_response = response.choices[0].message.content
                
                # --- Salva a playlist gerada no histórico ---
                nova_playlist = {"feeling": user_input, "playlist_md": ia_response}
                st.session_state.playlist_history.insert(0, nova_playlist)
                # --- FIM ---

                st.markdown("---")
                st.subheader("🎶 Sua Trilha Sonora Personalizada:")
                st.markdown(ia_response, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Ocorreu um erro ao chamar a IA do Groq: {e}")
    else:
        st.warning("Por favor, me diga como você está seindo!")


# --- NOVO: Seção para exibir o histórico (COM SELECTBOX) ---
st.markdown("---")
st.subheader("📖 Seu Histórico de Playlists")

if not st.session_state.playlist_history:
    st.caption("Suas playlists salvas aparecerão aqui depois que você gerar a primeira.")
else:
    # 1. Criar a lista de opções para o selectbox
    # (Usamos um truque com 'enumerate' para obter o índice 0, 1, 2...)
    option_list = []
    for i, item in enumerate(st.session_state.playlist_history):
        # Mostra a mais recente primeiro (índice 0)
        prefix = "Mais Recente: " if i == 0 else ""
        title = f"{prefix}Playlist para: \"{item['feeling'][:50]}...\""
        option_list.append(title)
    
    # 2. Mostrar o selectbox
    # 'index=0' garante que a "Mais Recente" seja selecionada por padrão
    selected_option = st.selectbox(
        "Selecione uma playlist para rever:",
        options=option_list,
        index=0,
        label_visibility="collapsed"
    )
    
    # 3. Encontrar a playlist que corresponde à opção selecionada
    # Pegamos o índice (0, 1, 2...) da opção na lista
    selected_index = option_list.index(selected_option)
    
    # 4. Mostrar o conteúdo da playlist selecionada
    st.markdown(
        st.session_state.playlist_history[selected_index]['playlist_md'],
        unsafe_allow_html=True
    )
    
# --- FIM DA NOVA SEÇÃO ---