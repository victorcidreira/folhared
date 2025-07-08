import streamlit as st
import os
import pandas as pd
import tempfile
import traceback
import io
from streamlit_option_menu import option_menu

# Importa as funções dos outros módulos do seu projeto
from extracao_pdf import gerar_txt_de_pdf
from processamento_dados import extract_employee_data, salvar_arquivo, ler_arquivo
from utils import criar_diretorio

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="FBC Consultoria", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO PARA UM LOOK PROFISSIONAL ---
def apply_custom_css():
    css = """
    <style>
    /* Importa uma fonte moderna do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Variáveis de cor */
    :root {
        --primary-bg: #f8fafc;
        --sidebar-bg: #1e293b;
        --sidebar-hover: #334155;
        --sidebar-selected: #0ea5e9;
        --sidebar-text: #cbd5e1;
        --sidebar-text-selected: #ffffff;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

    /* Sidebar personalizada - forçando fundo preto em todos os elementos */
    .css-1d391kg {
        background-color: var(--sidebar-bg) !important;
        width: 280px !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        width: 280px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--sidebar-bg) !important;
        width: 280px !important;
    }

    /* Força o fundo preto em todo conteúdo da sidebar */
    [data-testid="stSidebar"] .block-container {
        background-color: var(--sidebar-bg) !important;
    }

    [data-testid="stSidebar"] * {
        background-color: transparent !important;
    }

    /* Header da sidebar */
    .sidebar-header {
        padding: 2rem 1.5rem 1rem 1.5rem;
        border-bottom: 1px solid #334155;
        margin-bottom: 1rem;
        background-color: var(--sidebar-bg) !important;
    }
    
    .sidebar-title {
        color: #ffffff !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-subtitle {
        color: var(--sidebar-text) !important;
        font-size: 0.875rem;
        margin-top: 0.25rem;
        margin-bottom: 0;
    }

    /* Área principal */
    .main .block-container {
        padding: 2rem 3rem;
        background-color: var(--primary-bg);
        max-width: none;
    }

    /* Títulos das páginas */
    .page-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .page-description {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    /* Cards de conteúdo */
    .content-card {
        background-color: var(--card-bg);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }

    /* Botões personalizados */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgb(16 185 129 / 0.2);
        transition: all 0.2s ease;
        font-size: 1rem;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgb(16 185 129 / 0.3);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background-color: #f1f5f9;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Mensagens de status */
    .stAlert > div {
        border-radius: 8px;
        border: none;
        box-shadow: var(--shadow);
    }
    
    /* Spinner customizado */
    .stSpinner > div {
        border-top-color: var(--sidebar-selected) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- MÓDULOS DA APLICAÇÃO ---

def render_conversao_folha():
    """Renderiza a página do módulo de Conversão de Folha."""
    # Header da página
    st.markdown("""
        <div class="page-header">
            <h1 class="page-title">
                📄 Conversão de Folha de Pagamento
            </h1>
            <p class="page-description">
                Faça upload do arquivo PDF para converter em um relatório Excel
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Card principal
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Selecione o arquivo PDF", 
        type=["pdf"],
        help="Arraste e solte ou clique para carregar o arquivo PDF da folha de pagamento."
    )

    if uploaded_file is not None:
        with st.spinner("🔄 Processando o arquivo... Por favor, aguarde."):
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Salva o PDF temporariamente
                    pdf_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Gera arquivo de texto
                    txt_path = os.path.join(temp_dir, "resultado_extracao.txt")
                    gerar_txt_de_pdf(pdf_path, txt_path)

                    if not os.path.exists(txt_path):
                        st.error("❌ Falha ao gerar o arquivo de texto a partir do PDF.")
                        return

                    # Lê e processa os dados
                    text_data = ler_arquivo(txt_path)
                    if not text_data:
                        st.error("❌ O arquivo de texto gerado está vazio ou não pôde ser lido.")
                        return

                    employee_data = extract_employee_data(text_data)
                    if not employee_data:
                        st.error("❌ Nenhum dado de funcionário foi encontrado. Verifique o formato do PDF.")
                        return

                    # Cria DataFrame e arquivo Excel
                    df = pd.DataFrame(employee_data)
                    # Salva o DataFrame em um buffer de memória
                    excel_buffer = io.BytesIO()
                    salvar_arquivo(df, excel_buffer)
                    excel_buffer.seek(0)  # Reposiciona o cursor para o início do buffer
                    st.success("✅ Dados extraídos com sucesso!")
                    
                    # Mostra preview dos dados
                    with st.expander("👁️ Visualizar dados extraídos", expanded=False):
                        st.dataframe(df, use_container_width=True)

                    # Opção de download
                    download_option = st.radio(
                        "Como você gostaria de baixar o arquivo?",
                        ("Download Direto", "Salvar no Disco"),
                        index=0
                    )

                    if download_option == "Download Direto":
                        # Botão de download direto
                        excel_buffer.seek(0)  # Reposiciona o cursor para o início do buffer novamente
                        st.download_button(
                            label="📥 Baixar Relatório em Excel",
                            data=excel_buffer,
                            file_name="dados_funcionarios.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        # Salvar no disco (exemplo: na pasta 'dados/temp')
                        output_dir = os.path.join(os.getcwd(), "dados", "temp")
                        criar_diretorio(output_dir)
                        output_file_path = os.path.join(output_dir, "dados_funcionarios.xlsx")
                        salvar_arquivo(df, output_file_path)
                        st.success(f"Arquivo salvo em: {output_file_path}")

                except Exception as e:
                    st.error("❌ Ocorreu um erro inesperado durante o processamento:")
                    with st.expander("Ver detalhes do erro"):
                        st.code(traceback.format_exc())
    else:
        st.info("📋 Aguardando o carregamento de um arquivo PDF para iniciar o processo.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FUNÇÃO PRINCIPAL ---

def run_app():
    apply_custom_css()

    # Sidebar com navegação
    with st.sidebar:
        # Header da sidebar
        st.markdown("""
            <div class="sidebar-header">
                <h1 class="sidebar-title">Red Engenharia</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        selected_module = option_menu(
            menu_title=None,
            options=["Conversão Folha"],
            icons=["file-earmark-arrow-down"],
            default_index=0,
            styles={
                "container": {
                    "padding": "0px",
                    "background-color": "#1e293b",
                    "margin": "0px"
                },
                "icon": {
                    "color": "#cbd5e1",
                    "font-size": "1.2rem"
                },
                "nav-link": {
                    "font-size": "1rem",
                    "text-align": "left",
                    "margin": "4px 16px",
                    "padding": "12px 16px",
                    "border-radius": "8px",
                    "color": "#cbd5e1",
                    "background-color": "#1e293b",
                    "font-weight": "500",
                    "--hover-color": "#334155",
                    "white-space": "nowrap",
                    "overflow": "hidden",
                    "text-overflow": "ellipsis"
                },
                "nav-link-selected": {
                    "background-color": "#0ea5e9",
                    "color": "#ffffff",
                    "font-weight": "600",
                    "white-space": "nowrap",
                    "overflow": "hidden",
                    "text-overflow": "ellipsis"
                }
            }
        )
        
        # Rodapé da sidebar
        st.markdown("---")
        st.markdown("""
            <div style="padding: 1rem; text-align: center; color: #cbd5e1; font-size: 0.8rem;">
                Desenvolvido por FBC Consultoria Empresarial
            </div>
        """, unsafe_allow_html=True)

    # Roteamento de páginas
    if selected_module == "Conversão Folha":
        render_conversao_folha()

if __name__ == "__main__":
    run_app()