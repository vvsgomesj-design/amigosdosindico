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
from PIL import Image as PILImage

# --- 1. FUNÇÕES DE APOIO ---
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
    
    if os.path.exists('amigosdosindico.png'):
        try:
            logo = RLImage('amigosdosindico.png', width=4*cm, height=2*cm)
            elementos.append(logo)
        except: pass
        
    elementos.append(Paragraph(f"Relatório de Vistoria: {nome_predio}", estilos['Title']))
    elementos.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
    elementos.append(Spacer(1, 12))
    
    for chave, dados in respostas.items():
        if dados['status'] != "Pendente":
            cor = colors.green if dados['status'] == "Conforme" else colors.red
            estilo_st = ParagraphStyle('st', parent=estilos['Normal'], textColor=cor, fontWeight='Bold')
            elementos.append(Paragraph(f"<b>Item:</b> {dados['nome']}", estilos['Normal']))
            elementos.append(Paragraph(f"<b>Status:</b> {dados['status']}", estilo_st))
            if dados.get('obs'):
                elementos.append(Paragraph(f"<b>Observações:</b> {dados['obs']}", estilos['Normal']))
            
            # Adicionar foto ao PDF se existir
            if chave in fotos and fotos[chave]:
                try:
                    img_data = fotos[chave]
                    if hasattr(img_data, 'getvalue'): img_data = img_data.getvalue()
                    img_buffer = io.BytesIO(img_data)
                    pil_img = PILImage.open(img_buffer)
                    w, h = pil_img.size
                    aspect = h / w
                    elementos.append(RLImage(io.BytesIO(img_data), width=10*cm, height=10*cm*aspect))
                except: pass
                
            elementos.append(Spacer(1, 5))
            elementos.append(Paragraph("-" * 90, estilos['Normal']))
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- 2. CONFIGURAÇÃO ---
st.set_page_config(page_title="Amigos do Síndico PRO", layout="wide")
if 'respostas' not in st.session_state: st.session_state.respostas = {}
if 'fotos' not in st.session_state: st.session_state.fotos = {}
if 'pagina' not in st.session_state: st.session_state.pagina = "login"

# --- 3. ESTRUTURA DE CATEGORIAS ---
if 'categorias_dinamicas' not in st.session_state:
    cats = {
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
    # Personalizadas do 13 ao 17
    for i in range(13, 18):
        chave = f"{i}. Personalizada"
        cats[chave] = {"emoji": "📝", "itens": [{"desc": f"Subitem {j+1}", "norma": ""} for j in range(10)], "custom": True}
    st.session_state.categorias_dinamicas = cats

# --- 4. INTERFACE ---
if os.path.exists('amigosdosindico.png'):
    st.image('amigosdosindico.png', width=200)

dados_clientes = carregar_clientes()

if st.session_state.pagina == "login":
    senha = st.text_input("Senha do Condomínio:", type="password")
    if st.button("Entrar", use_container_width=True):
        if senha in dados_clientes:
            st.session_state.nome_predio = dados_clientes[senha]["nome_condominio"]
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("Senha incorreta.")

elif st.session_state.pagina == "menu":
    st.subheader(f"🏢 Vistoria: {st.session_state.nome_predio}")
    if st.button("📊 GERAR RELATÓRIO PDF", use_container_width=True):
        pdf = gerar_pdf_vistoria(st.session_state.nome_predio, st.session_state.respostas, st.session_state.fotos)
        st.download_button("⬇️ Baixar PDF", data=pdf, file_name=f"Vistoria_{st.session_state.nome_predio}.pdf")
    
    st.write("---")
    cols = st.columns(2)
    for i, (chave, info) in enumerate(st.session_state.categorias_dinamicas.items()):
        with cols[i % 2]:
            if info.get("custom"):
                nome_exib = st.text_input(f"Editar Título {chave[:2]}:", value=chave, key=f"t_{chave}")
                if st.button(f"Abrir: {nome_exib}", key=f"b_{chave}", use_container_width=True):
                    st.session_state.cat_ativa, st.session_state.cat_nome_atual = chave, nome_exib
                    st.session_state.pagina = "categoria"; st.rerun()
            else:
                if st.button(f"{info['emoji']} {chave}", use_container_width=True):
                    st.session_state.cat_ativa, st.session_state.cat_nome_atual = chave, chave
                    st.session_state.pagina = "categoria"; st.rerun()

elif st.session_state.pagina == "categoria":
    cat_chave = st.session_state.cat_ativa
    info = st.session_state.categorias_dinamicas[cat_chave]
    if st.button("← Menu"): st.session_state.pagina = "menu"; st.rerun()
    st.title(st.session_state.cat_nome_atual)

    for idx, item_data in enumerate(info["itens"]):
        res_id = f"{cat_chave}_{idx}"
        
        # Correção Visual: Garantir que apenas o texto da descrição apareça
        nome_item = st.text_input(f"Item {idx+1}:", value=item_data["desc"], key=f"in_{res_id}") if info.get("custom") else item_data["desc"]
        
        if not info.get("custom"):
            st.write(f"#### {idx+1}. {nome_item}")
            if "norma" in item_data: st.caption(f"📜 {item_data['norma']}")

        if res_id not in st.session_state.respostas:
            st.session_state.respostas[res_id] = {"status": "Pendente", "nome": nome_item, "obs": ""}
        st.session_state.respostas[res_id]["nome"] = nome_item

        c1, c2, c3 = st.columns([1, 1, 1.5])
        status = st.session_state.respostas[res_id]["status"]
        cor_status = "#28a745" if status == "Conforme" else "#dc3545" if status == "Irregular" else "#6c757d"

        with c1:
            if st.button("✅ CONFORME", key=f"ok_{res_id}", use_container_width=True):
                st.session_state.respostas[res_id]["status"] = "Conforme"; st.rerun()
        with c2:
            if st.button("❌ IRREGULAR", key=f"no_{res_id}", use_container_width=True):
                st.session_state.respostas[res_id]["status"] = "Irregular"; st.rerun()
        with c3:
            st.markdown(f'<div style="background-color:{cor_status};color:white;padding:12px;text-align:center;border-radius:10px;font-weight:bold;">{status.upper()}</div>', unsafe_allow_html=True)

        # Notas e Fotos de forma limpa
        st.session_state.respostas[res_id]["obs"] = st.text_area("Notas:", value=st.session_state.respostas[res_id]["obs"], key=f"o_{res_id}", height=80)
        
        up = st.file_uploader("📸 Anexar Foto", type=['jpg','png','jpeg'], key=f"up_{res_id}")
        if up: st.session_state.fotos[res_id] = up
        
        if res_id in st.session_state.fotos:
            st.image(st.session_state.fotos[res_id], width=200)
            if st.button("🗑️ Remover Foto", key=f"del_{res_id}"):
                st.session_state.fotos.pop(res_id); st.rerun()
        
        st.write("---")