import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ---------- CONFIGURAÇÕES ----------
EMAIL_DESTINO = "ianquelalves@gmail.com"
EMAIL_REMETENTE = "ianquelalves@gmail.com"
SENHA_REMETENTE = "fbqx ikou jwdg qepn"  # Gerada no Gmail

# Criar diretórios
os.makedirs("fotos", exist_ok=True)
os.makedirs("declaracoes", exist_ok=True)

# ---------- INTERFACE ----------
st.markdown(
    """
    <div style="text-align: center;">
        <img src="logo_guardioes.png" width="300">
        <h1>Cadastro de Atletas - Guardiões da Estácio</h1>
    </div>
    """,
    unsafe_allow_html=True
)

with st.form("formulario_cadastro"):
    nome = st.text_input("Nome Completo")
    rg = st.text_input("RG")
    orgao_emissor = st.text_input("Órgão Emissor")
    cpf = st.text_input("CPF")
    data_nascimento = st.date_input(
        "Data de Nascimento",
        min_value=datetime(1980, 1, 1),
        max_value=datetime(2025, 12, 31)
    )
    foto = st.file_uploader("Foto (JPG)", type=["jpg", "jpeg"])
    declaracao = st.file_uploader("Declaração (PDF)", type=["pdf"])

    enviado = st.form_submit_button("Enviar Cadastro")

    if enviado:
        if not all([nome, rg, orgao_emissor, cpf, data_nascimento, foto, declaracao]):
            st.error("⚠️ Preencha todos os campos e envie os arquivos.")
        else:
            dados = {
                "Data": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Nome": [nome],
                "RG": [rg],
                "Órgão Emissor": [orgao_emissor],
                "CPF": [cpf],
                "Data de Nascimento": [data_nascimento.strftime("%d/%m/%Y")],
            }

            df = pd.DataFrame(dados)
            csv_path = "cadastros.csv"
            if os.path.exists(csv_path):
                df.to_csv(csv_path, mode="a", header=False, index=False)
            else:
                df.to_csv(csv_path, index=False)

            foto_path = os.path.join("fotos", f"{cpf}_{foto.name}")
            declaracao_path = os.path.join("declaracoes", f"{cpf}_{declaracao.name}")
            with open(foto_path, "wb") as f:
                f.write(foto.read())
            with open(declaracao_path, "wb") as f:
                f.write(declaracao.read())

            # ---------- ENVIO DE EMAIL ----------
            msg = EmailMessage()
            msg['Subject'] = f"Novo Cadastro: {nome}"
            msg['From'] = EMAIL_REMETENTE
            msg['To'] = EMAIL_DESTINO
            msg.set_content(f"""
Novo atleta cadastrado:

Nome: {nome}
CPF: {cpf}
RG: {rg}
Data de Nascimento: {data_nascimento.strftime('%d/%m/%Y')}
""")

            with open(csv_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="csv", filename="cadastros.csv")
            with open(foto_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="jpeg", filename=os.path.basename(foto_path))
            with open(declaracao_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(declaracao_path))

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
                    smtp.send_message(msg)
                st.success("✅ Cadastro e documentos enviados com sucesso!")
            except Exception as e:
                st.warning("Cadastro salvo, mas erro ao enviar e-mail com anexos.")
                st.text(str(e))
