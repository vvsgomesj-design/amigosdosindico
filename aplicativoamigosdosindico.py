import streamlit as st
import json
import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.units import cm

# --- 1. FUNÇÃO PARA CARREGAR DADOS ---
def carregar_clientes():
    if os.path.exists('clientes.json'):
        with open('clientes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def gerar_pdf_vistoria(nome_predio, respostas, fotos):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    estilos = getSampleStyleSheet()
    elementos = []

    # Título do Relatório
    titulo = f"Relatório de Vistoria: {nome_predio}"
    elementos.append(Paragraph(titulo, estilos['Title']))
    elementos.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
    elementos.append(Spacer(1, 12))

    for chave, dados in respostas.items():
        if dados['status'] != "Pendente":
            # Cabeçalho do Item
            cor_texto = colors.green if dados['status'] == "Conforme" else colors.red
            estilo_status = ParagraphStyle('item', parent=estilos['Normal'], textColor=cor_texto, fontWeight='Bold')
            
            elementos.append(Paragraph(f"<b>Item:</b> {dados['nome']}", estilos['Normal']))
            elementos.append(Paragraph(f"<b>Status:</b> {dados['status']}", estilo_status))
            
            if dados.get('obs'):
                elementos.append(Paragraph(f"<b>Observações:</b> {dados['obs']}", estilos['Normal']))
            
            if chave in fotos:
                img_data = fotos[chave].getvalue()
                img = RLImage(io.BytesIO(img_data), width=8*cm, height=6*cm)
                elementos.append(img)
            
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph("-" * 90, estilos['Normal']))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Amigos do Síndico PRO", layout="wide")

# --- 3. INICIALIZAÇÃO DE ESTADOS ---
if 'respostas' not in st.session_state: st.session_state.respostas = {}
if 'fotos' not in st.session_state: st.session_state.fotos = {}
if 'pagina' not in st.session_state: st.session_state.pagina = "login"

# --- 4. CATEGORIAS (ESTRUTURA COMPLETA) ---
if 'categorias_dinamicas' not in st.session_state:
   categorias = {
    "01. Elétrica": {
        "emoji": "⚡",
        "itens": [
            {"desc": "Quadro geral de energia", "norma": "NBR 5410", "detalhe": "Exige proteção contra choques. Quadros devem estar limpos e identificados."},
            {"desc": "Disjuntores", "norma": "NR-10", "detalhe": "Devem ser testados para evitar aquecimento da fiação e risco de incêndio."},
            {"desc": "Iluminação de emergência", "norma": "NBR 10898", "detalhe": "Deve garantir a saída segura. Teste mensal é obrigatório."},
            {"desc": "Aterramento / SPDA", "norma": "NBR 5419", "detalhe": "O para-raios deve ter medição anual. Falha causa queima de aparelhos."},
            {"desc": "Cabos aparentes", "norma": "NR-10", "detalhe": "Inspecionar quanto a desgaste, emendas irregulares e exposição."},
            {"desc": "Gerador (se houver)", "norma": "NBR 15984", "detalhe": "Teste mensal com carga. Verificar nível de combustível e baterias."}
        ]
    },
    "02. Hidráulica": {
        "emoji": "💧",
        "itens": [
            {"desc": "Bombas de água", "norma": "NBR 5674", "detalhe": "Manutenção preventiva evita interrupção do abastecimento."},
            {"desc": "Reservatórios de água", "norma": "Portaria 2914 MS", "detalhe": "Inspeção visual semestral. Verificar tampas, limpeza e vazamentos."},
            {"desc": "Vazamentos em tubulações", "norma": "NBR 15575", "detalhe": "Vazamentos causam desperdício e infiltrações. Inspecionar conexões."},
            {"desc": "Pressão da água", "norma": "NBR 5626", "detalhe": "Pressão inadequada danifica tubulações. Medir em pontos críticos."},
            {"desc": "Registros gerais", "norma": "NBR 5674", "detalhe": "Devem operar livremente. Verificar corrosão e vedação."},
            {"desc": "Drenagem", "norma": "NBR 8160", "detalhe": "Sistemas de drenagem devem estar desobstruídos para evitar alagamentos."},
            {"desc": "Esgoto", "norma": "NBR 8160", "detalhe": "Inspecionar odores e refluxos. Verificar caixas de inspeção."},
            {"desc": "Limpeza da caixa d'água", "norma": "Portaria 2914 MS", "detalhe": "Obrigatoriedade semestral. A falta gera multa e risco à saúde."}
        ]
    },
    "03. Combate a Incêndio": {
        "emoji": "🔥",
        "itens": [
            {"desc": "Validade dos extintores", "norma": "NBR 12693", "detalhe": "Verificar carga, pressão e prazo de recarga. Troca imediata se vencido."},
            {"desc": "Hidrantes", "norma": "NBR 13714", "detalhe": "Inspecionar mangueiras, esguichos e registro. Teste de vazão anual."},
            {"desc": "Alarmes de incêndio", "norma": "NBR 17240", "detalhe": "Teste mensal dos acionadores e sirenes. Manter central em funcionamento."},
            {"desc": "Sinalização de emergência", "norma": "NBR 13434", "detalhe": "Placas devem estar visíveis e iluminadas. Substituir se danificadas."},
            {"desc": "Rotas de fuga", "norma": "NBR 9077", "detalhe": "Corredores livres, portas abrem no sentido da saída. Simulação anual."},
            {"desc": "Portas corta-fogo", "norma": "NBR 11742", "detalhe": "Devem fechar sozinhas. Verificar molas, borrachas e vedação."}
        ]
    },
    "04. Estrutural e Fachada": {
        "emoji": "🏢",
        "itens": [
            {"desc": "Rachaduras", "norma": "NBR 15575", "detalhe": "Monitorar evolução. Rachaduras em vigas ou pilares exigem laudo técnico."},
            {"desc": "Infiltrações", "norma": "NBR 15575", "detalhe": "Manchas, bolhas ou mofo indicam falhas na impermeabilização."},
            {"desc": "Desprendimento de revestimento", "norma": "NBR 13749", "detalhe": "Risco de queda. Inspecionar pastilhas, reboco e textura."},
            {"desc": "Pintura", "norma": "NBR 5674", "detalhe": "Desgaste e descascamento expõem a alvenaria. Programar repintura."},
            {"desc": "Juntas de dilatação", "norma": "NBR 9050", "detalhe": "Devem estar limpas e com material flexível. Trincas comprometem a estrutura."},
            {"desc": "Sacadas", "norma": "NBR 16239", "detalhe": "Verificar corrimãos, guarda-corpos e drenagem. Risco de queda."}
        ]
    },
    "05. Cobertura e Telhado": {
        "emoji": "🏠",
        "itens": [
            {"desc": "Telhas quebradas", "norma": "NBR 15210", "detalhe": "Substituir imediatamente para evitar infiltrações."},
            {"desc": "Calhas", "norma": "NBR 10844", "detalhe": "Limpar regularmente. Verificar desobstrução e fixação."},
            {"desc": "Ralos", "norma": "NBR 10844", "detalhe": "Manter desobstruídos. Testar com água para verificar escoamento."},
            {"desc": "Impermeabilização", "norma": "NBR 9575", "detalhe": "Inspecionar bolhas, trincas ou descolamento. Revisão periódica."},
            {"desc": "Estruturas metálicas", "norma": "NBR 8800", "detalhe": "Verificar corrosão e conexões. Pintura de proteção necessária."}
        ]
    },
    "06. Áreas Comuns": {
        "emoji": "🌳",
        "itens": [
            {"desc": "Iluminação", "norma": "NBR 5410", "detalhe": "Lâmpadas queimadas devem ser trocadas. Verificar acionamento."},
            {"desc": "Pisos", "norma": "NBR 9050", "detalhe": "Inspecionar desníveis, rachaduras e desgaste. Risco de quedas."},
            {"desc": "Corrimãos", "norma": "NBR 9050", "detalhe": "Devem estar firmes e na altura correta. Verificar fixação."},
            {"desc": "Limpeza", "norma": "Boas práticas", "detalhe": "Manter áreas comuns limpas evita proliferação de pragas."},
            {"desc": "Portas", "norma": "NBR 15930", "detalhe": "Verificar fechaduras, dobradiças e vedação."},
            {"desc": "Ventilação", "norma": "NBR 16401", "detalhe": "Garantir renovação de ar. Limpar grelhas e filtros."},
            {"desc": "Segurança geral", "norma": "Boas práticas", "detalhe": "Observar condições de uso, como pisos escorregadios ou obstáculos."}
        ]
    },
    "07. Garagem e Estacionamento": {
        "emoji": "🚗",
        "itens": [
            {"desc": "Iluminação", "norma": "NBR 5410", "detalhe": "Iluminação adequada para circulação de veículos e pessoas."},
            {"desc": "Sinalização", "norma": "CTB / NBR 13434", "detalhe": "Placas de velocidade, faixas e vagas devem estar visíveis."},
            {"desc": "Piso", "norma": "NBR 9050", "detalhe": "Verificar desgaste, buracos e pintura de vagas."},
            {"desc": "Ventilação", "norma": "NBR 16401", "detalhe": "Sistemas de exaustão devem funcionar para evitar acúmulo de gases."}
        ]
    },
    "08. Playground e Equipamentos de Lazer": {
        "emoji": "🛝",
        "itens": [
            {"desc": "Parafusos e fixações", "norma": "NBR 16071", "detalhe": "Apertar e verificar ausência de partes soltas."},
            {"desc": "Estrutura", "norma": "NBR 16071", "detalhe": "Inspecionar trincas, empenamentos e estabilidade."},
            {"desc": "Piso de proteção", "norma": "NBR 16071", "detalhe": "Piso emborrachado deve estar íntegro para amortecer quedas."},
            {"desc": "Ferrugem", "norma": "NBR 16071", "detalhe": "Partes metálicas oxidadas podem quebrar. Lixar e pintar."},
            {"desc": "Cordas e correntes", "norma": "NBR 16071", "detalhe": "Verificar desgaste, nós e resistência."},
            {"desc": "Estabilidade", "norma": "NBR 16071", "detalhe": "Balançar equipamentos para testar firmeza no solo."}
        ]
    },
    "09. Elevadores": {
        "emoji": "🛗",
        "itens": [
            {"desc": "Contrato de manutenção de elevadores", "norma": "NBR 16046", "detalhe": "Manter contrato ativo com empresa credenciada. Verificar ART."},
            {"desc": "Planejamento de revisão de elevadores", "norma": "NBR 5674", "detalhe": "Programar manutenções preventivas conforme periodicidade do fabricante."}
        ]
    },
    "10. Documentação e Legal": {
        "emoji": "📄",
        "itens": [
            {"desc": "Laudo elétrico", "norma": "NR-10", "detalhe": "Exigido em condomínios. Deve ser renovado a cada 5 anos."},
            {"desc": "Laudo SPDA", "norma": "NBR 5419", "detalhe": "Medição de resistência de aterramento anual."},
            {"desc": "AVCB", "norma": "Lei Estadual", "detalhe": "Auto de Vistoria do Corpo de Bombeiros. Manter válido."},
            {"desc": "Seguro do condomínio", "norma": "Código Civil", "detalhe": "Incêndio e responsabilidade civil. Verificar cobertura."},
            {"desc": "Atas de assembleias", "norma": "Código Civil", "detalhe": "Registrar decisões e aprovações de obras e contas."},
            {"desc": "Contratos de manutenção", "norma": "Boas práticas", "detalhe": "Organizar contratos vigentes (limpeza, segurança, etc.)."},
            {"desc": "Organizar arquivos", "norma": "Boas práticas", "detalhe": "Manter documentos técnicos e administrativos em ordem."}
        ]
    },
    "11. Planejamento de Manutenção": {
        "emoji": "📅",
        "itens": [
            {"desc": "Planejar manutenção elétrica", "norma": "NBR 5674", "detalhe": "Cronograma anual de inspeções e testes."},
            {"desc": "Planejar manutenção hidráulica", "norma": "NBR 5674", "detalhe": "Definir datas para limpeza de caixas e revisão de bombas."},
            {"desc": "Planejar pintura predial", "norma": "NBR 5674", "detalhe": "Estimar periodicidade conforme exposição e material."},
            {"desc": "Planejar inspeção estrutural", "norma": "NBR 5674", "detalhe": "Contratar engenheiro para vistorias periódicas."},
            {"desc": "Programar limpeza caixa d'água", "norma": "Portaria 2914 MS", "detalhe": "Agendar limpezas semestrais e registrar."},
            {"desc": "Programar revisão de bombas", "norma": "NBR 5674", "detalhe": "Manutenção preventiva a cada 6 meses."},
            {"desc": "Registrar cronograma", "norma": "Boas práticas", "detalhe": "Manter planilha com datas e responsáveis."}
        ]
    },
    "12. Controle de Acesso e Monitoramento": {
        "emoji": "📹",
        "itens": [
            {"desc": "Portão de entrada automático", "norma": "NR-12", "detalhe": "Verificar sensores, motor e sistema de abertura. Testar reversão."},
            {"desc": "Portão de garagem", "norma": "NR-12", "detalhe": "Inspecionar trilhos, roldanas e dispositivos de segurança."},
            {"desc": "Câmeras de segurança", "norma": "Boas práticas", "detalhe": "Testar funcionamento, gravação e ângulo de cobertura."}
        ]
    }
}
    # Acrescentar as 5 categorias personalizadas
categorias = {} # Substitua por seu dicionário completo
for i in range(1, 6):
        nome_chave = f"Personalizada {i}"
        categorias[nome_chave] = {"emoji": "📝", "itens": [{"desc": f"Item {j+1}"} for j in range(10)]}
        st.session_state.categorias_dinamicas = categorias

# --- 5. LOGIN ---
dados_clientes = carregar_clientes()
if "autenticado" not in st.session_state:
    st.title("🔑 Login Amigos do Síndico")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha in dados_clientes:
            st.session_state.autenticado = True
            st.session_state.nome_predio = dados_clientes[senha]["nome_condominio"]
            # --- 6. INTERFACE ---
# --- 6. INTERFACE ---
if st.session_state.pagina == "menu":
    st.subheader(f"🏢 {st.session_state.nome_predio}")
    
    st.divider() # Linha 196 corrigida aqui
    st.subheader("📄 Finalizar Vistoria")
    
    if st.button("📊 Gerar Relatório PDF", use_container_width=True):
        if not st.session_state.respostas:
            st.warning("Realize ao menos uma vistoria antes de gerar o relatório.")
        else:
            pdf = gerar_pdf_vistoria(
                st.session_state.nome_predio, 
                st.session_state.respostas, 
                st.session_state.fotos
            )
            
            st.download_button(
                label="⬇️ Baixar Relatório PDF",
                data=pdf,
                file_name=f"Vistoria_{st.session_state.nome_predio}.pdf",
                mime="application/pdf",
                use_container_width=True
            )    

    # Exibição das categorias em grade
    cols = st.columns(2)
    for i, cat_id in enumerate(st.session_state.categorias_dinamicas.keys()):
        with cols[i % 2]:
            if "Personalizada" in cat_id:
                label_atual = st.session_state.get(f"nome_real_{cat_id}", cat_id)
                novo_nome = st.text_input(f"Editar nome da {cat_id}:", value=label_atual, key=f"edit_{cat_id}")
                st.session_state[f"nome_real_{cat_id}"] = novo_nome
                btn_txt = f"📝 {novo_nome}"
            else:
                btn_txt = f"{st.session_state.categorias_dinamicas[cat_id]['emoji']} {cat_id}"

            if st.button(btn_txt, use_container_width=True, key=f"btn_{cat_id}"):
                st.session_state.cat_ativa = cat_id
                st.session_state.pagina = "categoria"
                st.rerun()

elif st.session_state.pagina == "categoria":
    cat = st.session_state.cat_ativa
    nome_exibicao = st.session_state.get(f"nome_real_{cat}", cat)
    st.title(f"Vistoria: {nome_exibicao}")
    
    if st.button("← Voltar"):
        st.session_state.pagina = "menu"; st.rerun()

    for i, item in enumerate(st.session_state.categorias_dinamicas[cat]["itens"]):
        chave = f"{cat}_item_{i}"
        
        if chave not in st.session_state.respostas:
            st.session_state.respostas[chave] = {"status": "Pendente", "obs": "", "nome": item['desc']}

        st.write(f"---")
        if "Personalizada" in cat:
            nome_sub = st.text_input(f"Nome do Item {i+1}:", value=st.session_state.respostas[chave]["nome"], key=f"input_{chave}")
            st.session_state.respostas[chave]["nome"] = nome_sub
        else:
            st.write(f"### {st.session_state.respostas[chave]['nome']}")
        
        status_atual = st.session_state.respostas[chave]["status"]
        cor_fundo = "#28a745" if status_atual == "Conforme" else "#dc3545" if status_atual == "Irregular" else "#6c757d"

        col_v, col_r, col_status = st.columns([1, 1, 2])
        with col_v:
            if st.button("✅ CONFORME", key=f"v_{chave}", use_container_width=True):
                st.session_state.respostas[chave]["status"] = "Conforme"; st.rerun()
        with col_r:
            if st.button("❌ IRREGULAR", key=f"r_{chave}", use_container_width=True):
                st.session_state.respostas[chave]["status"] = "Irregular"; st.rerun()
        with col_status:
            st.markdown(f'<div style="background-color:{cor_fundo};color:white;padding:30px;text-align:center;border-radius:10px;font-weight:bold;">{status_atual.upper()}</div>', unsafe_allow_html=True)

        c_obs, c_foto = st.columns(2)
        with c_obs:
            obs_v = st.session_state.respostas[chave].get("obs", "")
            st.session_state.respostas[chave]["obs"] = st.text_area("Notas:", value=obs_v, key=f"txt_{chave}")
        with c_foto:
            arq = st.file_uploader("Anexar Foto", type=['jpg','png','jpeg'], key=f"up_{chave}")
            if arq:
                st.session_state.fotos[chave] = arq
                st.image(arq, width=150)