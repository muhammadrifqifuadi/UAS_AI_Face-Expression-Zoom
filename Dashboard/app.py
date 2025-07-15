import streamlit as st
import pandas as pd
import altair as alt
import time
import os

LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "expression_log.csv"))

st.set_page_config(page_title="Live Emotion Tracker", layout="wide")
st.title("📊 Real-time Emotion Dashboard")

placeholder = st.empty()

if not os.path.isfile(LOG_FILE):
    st.warning("Log file belum ditemukan. Jalankan detektor ekspresi dulu.")
else:
    st.sidebar.markdown("### 🔁 Refresh interval")
    interval = st.sidebar.slider("Detik per refresh", 1, 30, 5)

    try:
        df = pd.read_csv(LOG_FILE)

        if 'timestamp' not in df.columns:
            st.error("Kolom 'timestamp' tidak ditemukan dalam file log. Kolom tersedia: " + ", ".join(df.columns))
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            with placeholder.container():
                col1, col2 = st.columns([2, 1])

                chart = (
                    alt.Chart(df)
                    .mark_line(point=True)
                    .encode(
                        x='timestamp:T',
                        y='count():Q',
                        color='expression:N',
                        tooltip=['timestamp:T', 'expression:N']
                    )
                    .properties(height=400, title='Tren Ekspresi dari Waktu ke Waktu')
                )
                col1.altair_chart(chart, use_container_width=True)

                if 'face_id' in df.columns:
                    chart_by_student = (
                        alt.Chart(df)
                        .mark_line()
                        .encode(
                            x='timestamp:T',
                            y='count():Q',
                            color='face_id:N',
                            strokeDash='expression:N',
                            tooltip=['timestamp:T', 'face_id:N', 'expression:N']
                        )
                        .properties(height=300, title='Tren Ekspresi per Siswa (face_id)')
                    )
                    col1.altair_chart(chart_by_student, use_container_width=True)

                recent = df[df['timestamp'] > df['timestamp'].max() - pd.Timedelta(minutes=1)]
                summary = recent['expression'].value_counts().reset_index()
                summary.columns = ['Expression', 'Count']
                col2.write("### Ekspresi Terakhir (1 menit)")
                col2.dataframe(summary)

            time.sleep(interval)
            st.rerun()
    except Exception as e:
        st.error(f"Gagal memuat file log: {e}")
