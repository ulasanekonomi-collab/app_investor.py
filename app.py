import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import matplotlib
matplotlib.use('Agg')

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="ROI Villa Investor", layout="wide")

st.title("📊 ROI Simulator — Investor Grade")

# ========================
# SIDEBAR INPUT
# ========================
st.sidebar.header("Parameter Investasi")

investment = st.sidebar.number_input("Total Investasi (Rp)", value=120000000)
unit_price = st.sidebar.number_input("Harga 1 Unit Vila (Rp)", value=1200000000)

occupancy = st.sidebar.slider("Occupancy (%)", 30, 90, 60)
price = st.sidebar.number_input("Harga per Malam (Rp)", value=1200000)
days = st.sidebar.number_input("Hari Operasional", value=365)

share = st.sidebar.slider("Share Investor (%)", 10, 100, 60)
cost_ratio = st.sidebar.slider("Biaya Operasional (%)", 0, 80, 30) / 100

# ========================
# CALCULATION
# ========================
ownership = investment / unit_price if unit_price > 0 else 0

revenue = occupancy / 100 * price * days
income = revenue * (1 - cost_ratio) * (share / 100) * ownership
roi = (income / investment) * 100 if investment > 0 else 0
payback = investment / income if income > 0 else 0

# ========================
# METRICS
# ========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"Rp {revenue:,.0f}")
col2.metric("Income", f"Rp {income:,.0f}")
col3.metric("ROI (%)", f"{roi:.2f}%")
col4.metric("Payback (tahun)", f"{payback:.1f}")

st.caption(f"Kepemilikan Anda: {ownership*100:.2f}% dari 1 unit vila")

# ========================
# CHART FUNCTIONS (SAFE)
# ========================
def create_sensitivity_chart(price, days, cost_ratio, share, ownership, investment):
    fig, ax = plt.subplots()

    occ_range = np.linspace(30, 90, 50)
    roi_list = []

    for occ in occ_range:
        rev = occ / 100 * price * days
        inc = rev * (1 - cost_ratio) * (share / 100) * ownership
        r = (inc / investment) * 100 if investment > 0 else 0
        roi_list.append(r)

    ax.plot(occ_range, roi_list)
    ax.axhline(10, linestyle="--")
    ax.axhline(5, linestyle="--")
    ax.set_title("Sensitivity ROI")
    ax.set_xlabel("Occupancy (%)")
    ax.set_ylabel("ROI (%)")

    return fig


def create_distribution_chart(price, days, cost_ratio, share, ownership, investment, occupancy):
    fig, ax = plt.subplots()

    roi_sim = []

    for _ in range(1000):
        occ_sim = np.random.normal(occupancy, 10)
        occ_sim = max(0, min(100, occ_sim))

        rev = occ_sim / 100 * price * days
        inc = rev * (1 - cost_ratio) * (share / 100) * ownership
        r = (inc / investment) * 100 if investment > 0 else 0
        roi_sim.append(r)

    ax.hist(roi_sim, bins=30)
    ax.axvline(np.mean(roi_sim), linestyle="--")
    ax.set_title("Distribusi ROI")
    ax.set_xlabel("ROI (%)")

    return fig, roi_sim

# ========================
# DISPLAY CHART (ANTI ERROR)
# ========================
colA, colB = st.columns(2)

with colA:
    fig1 = create_sensitivity_chart(price, days, cost_ratio, share, ownership, investment)
    st.pyplot(fig1)
    plt.close(fig1)

with colB:
    fig2, roi_sim = create_distribution_chart(
    price, days, cost_ratio, share, ownership, investment, occupancy
)
    st.pyplot(fig2)
    plt.close(fig2)

# ========================
# INTERPRETASI
# ========================
if roi < 5:
    st.warning("ROI di bawah deposito")
elif roi < 10:
    st.info("ROI moderat dan stabil")
else:
    st.success("ROI menarik sebagai passive income")

# ========================
# AUTO NARASI
# ========================
narasi = f"""
Berdasarkan hasil simulasi, investasi sebesar Rp {investment:,.0f} 
menghasilkan pendapatan tahunan sekitar Rp {income:,.0f} dengan tingkat 
pengembalian investasi (ROI) sebesar {roi:.2f}%. 

Dengan asumsi tingkat okupansi {occupancy}%, biaya operasional {cost_ratio*100:.0f}%, 
dan skema bagi hasil {share}%, investasi ini memiliki periode pengembalian modal 
sekitar {payback:.1f} tahun.

Distribusi simulasi menunjukkan bahwa ROI cenderung berada di kisaran 
{np.mean(roi_sim):.2f}% dengan variasi moderat, sehingga investasi ini 
dapat dikategorikan sebagai instrumen dengan risiko menengah dan potensi 
imbal hasil yang relatif stabil.
"""

st.subheader("🧠 Narasi Otomatis")
st.write(narasi)

# ========================
# PDF GENERATOR (SAFE)
# ========================
def create_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("LAPORAN SIMULASI INVESTASI VILA", styles["Title"]))
    content.append(Spacer(1, 20))

    # generate fresh charts
    fig1 = create_sensitivity_chart()
    fig2, _ = create_distribution_chart(
    price, days, cost_ratio, share, ownership, investment, occupancy
)

    img_buffer1 = io.BytesIO()
    fig1.savefig(img_buffer1, format='png')
    img_buffer1.seek(0)
    plt.close(fig1)

    img_buffer2 = io.BytesIO()
    fig2.savefig(img_buffer2, format='png')
    img_buffer2.seek(0)
    plt.close(fig2)

    content.append(Paragraph("Sensitivity Analysis", styles["Heading2"]))
    content.append(Image(img_buffer1, width=400, height=250))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Distribusi ROI", styles["Heading2"]))
    content.append(Image(img_buffer2, width=400, height=250))

    doc.build(content)
    buffer.seek(0)
    return buffer

pdf = create_pdf()

st.download_button(
    label="📥 Download Laporan PDF",
    data=pdf,
    file_name="laporan_investasi_vila.pdf",
    mime="application/pdf"
)
