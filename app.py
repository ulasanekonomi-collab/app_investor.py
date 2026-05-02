import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="ROI Villa Investor", layout="wide")

st.title("📊 ROI Simulator – Investor Grade")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Parameter Investasi")

investment = st.sidebar.number_input("Total Investasi (Rp)", value=120000000)
unit_price = st.sidebar.number_input("Harga 1 Unit Vila (Rp)", value=1200000000)

occupancy = st.sidebar.slider("Occupancy (%)", 0, 100, 60)
price = st.sidebar.number_input("Harga per Malam (Rp)", value=1200000)
days = st.sidebar.number_input("Hari Operasional", value=365)

share = st.sidebar.slider("Share Investor (%)", 0, 100, 60)
cost_ratio = st.sidebar.slider("Biaya Operasional (%)", 0, 80, 30) / 100

# =========================
# MODEL
# =========================
ownership = investment / unit_price if unit_price > 0 else 0
revenue = occupancy / 100 * price * days
income = revenue * (1 - cost_ratio) * share / 100 * ownership
roi = (income / investment) * 100 if investment > 0 else 0

# =========================
# PAYBACK PERIOD
# =========================
if income > 0:
    payback = investment / income
else:
    payback = 0

# =========================
# IRR SIMULATION (10 tahun)
# =========================
cashflow = [-investment] + [income]*10

try:
    irr = np.irr(cashflow) * 100
except:
    irr = 0

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"Rp {revenue:,.0f}")
col2.metric("Income", f"Rp {income:,.0f}")
col3.metric("ROI (%)", f"{roi:.2f}%")
col4.metric("Payback (tahun)", f"{payback:.1f}")

st.write(f"📈 IRR (10 tahun): **{irr:.2f}%**")

# =========================
# SENSITIVITY
# =========================
occ_range = np.arange(30, 91, 5)
roi_list = []

for occ in occ_range:
    rev = occ / 100 * price * days
    inc = rev * (1 - cost_ratio) * share / 100 * ownership
    r = (inc / investment) * 100 if investment > 0 else 0
    roi_list.append(r)

fig1, ax1 = plt.subplots()
ax1.plot(occ_range, roi_list)
ax1.axhline(5, linestyle="--")
ax1.axhline(10, linestyle="--")
ax1.set_title("Sensitivity ROI")
ax1.set_xlabel("Occupancy (%)")
ax1.set_ylabel("ROI (%)")

# =========================
# PROBABILITY
# =========================
roi_sim = []

for _ in range(500):
    occ = np.random.normal(occupancy, 10)
    occ = np.clip(occ, 0, 100)
    
    rev = occ / 100 * price * days
    inc = rev * (1 - cost_ratio) * share / 100 * ownership
    r = (inc / investment) * 100 if investment > 0 else 0
    
    roi_sim.append(r)

fig2, ax2 = plt.subplots()
ax2.hist(roi_sim, bins=20)
ax2.axvline(5, linestyle="--")
ax2.axvline(10, linestyle="--")
ax2.set_title("Distribusi ROI")

colA, colB = st.columns(2)
colA.pyplot(fig1)
colB.pyplot(fig2)

# =========================
# PDF EXPORT
# =========================
def create_pdf(fig1, fig2):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("LAPORAN INVESTASI VILA", styles["Title"]))
    content.append(Spacer(1, 20))

    fig1.savefig("sens.png")
    fig2.savefig("prob.png")

    content.append(Paragraph("Sensitivity Analysis", styles["Heading2"]))
    content.append(Image("sens.png", width=400, height=250))

    content.append(Spacer(1, 20))

    content.append(Paragraph("Probabilitas ROI", styles["Heading2"]))
    content.append(Image("prob.png", width=400, height=250))

    doc.build(content)
    buffer.seek(0)
    return buffer

pdf = create_pdf(fig1, fig2)

st.download_button(
    label="📥 Download Laporan PDF",
    data=pdf,
    file_name="laporan_investasi.pdf",
    mime="application/pdf"
)
