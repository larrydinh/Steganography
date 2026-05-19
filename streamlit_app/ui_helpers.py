import html
import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --stego-primary: #ff4b4b;
            --stego-navy: #20243a;
            --stego-muted: #6b7280;
            --stego-card: #ffffff;
            --stego-soft: #f7f8fb;
            --stego-border: #e5e7eb;
        }
        .block-container {padding-top: 4rem; padding-bottom: 4rem; max-width: 1180px;}
        
        [data-testid="stSidebar"] {
            background: #020817;
            border-right: 1px solid #1E293B;
        }

        [data-testid="stSidebarNav"] {
            background: #020817;
        }

        [data-testid="stSidebarNav"] ul {
            padding-top: 1rem;
        }

        [data-testid="stSidebarNav"] a {
            background-color: transparent;
            color: #E5E7EB;
            border-radius: 12px;
            margin-bottom: 6px;
            transition: all 0.2s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #111827;
            color: white;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #1E293B;
            color: white;
            font-weight: 700;
        }
        [data-testid="stSidebarNav"] ul {padding-top: 1rem;}
        h1, h2, h3 {color: var(--stego-navy); letter-spacing: -0.03em;}
        .hero-card {
            padding: 2.2rem 2.4rem;
            border: 1px solid var(--stego-border);
            border-radius: 22px;
            background: linear-gradient(135deg, #ffffff 0%, #f7f9ff 55%, #fff4f4 100%);
            box-shadow: 0 18px 45px rgba(30, 35, 60, 0.08);
            margin-bottom: 1.25rem;
        }
        .hero-title {font-size: 3rem; line-height: 1.06; font-weight: 800; color: var(--stego-navy); margin-bottom: .6rem;}
        .hero-subtitle {font-size: 1.08rem; color: #4b5563; max-width: 860px; margin-bottom: 1rem;}
        .pill-row {display:flex; gap:.55rem; flex-wrap:wrap; margin-top: 1rem;}
        .pill {padding:.42rem .72rem; border-radius:999px; background:#eef2ff; color:#303655; font-size:.88rem; font-weight:600;}
        .mini-card {
            min-height: 145px;
            padding: 1.2rem;
            border: 1px solid var(--stego-border);
            border-radius: 18px;
            background: var(--stego-card);
            box-shadow: 0 10px 30px rgba(20, 24, 40, 0.05);
        }
        .mini-card h3 {font-size: 1.05rem; margin: .2rem 0 .35rem 0;}
        .mini-card p {font-size: .92rem; color: var(--stego-muted); margin: 0;}
        .step-number {display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:10px; background:#ffeded; color:#b91c1c; font-weight:800; margin-bottom:.5rem;}
        .section-note {color: var(--stego-muted); font-size: .94rem; margin-top: -.45rem; margin-bottom: 1rem;}
        .status-card {padding: 1rem; border-radius: 16px; background:#ecfdf5; border:1px solid #bbf7d0; color:#166534; font-weight:700;}
        .method-card {padding: .85rem 1rem; border-radius: 14px; border:1px solid var(--stego-border); background:#fafafa; height:100%;}
        .method-card strong {color:var(--stego-navy);}
        .method-card span {display:block; color:var(--stego-muted); font-size:.86rem; margin-top:.2rem;}
        .result-banner {padding:1.2rem 1.4rem; border-radius:18px; border:1px solid #bbf7d0; background:#f0fdf4; color:#14532d; margin-bottom:1rem;}
        .danger-banner {padding:1.1rem 1.2rem; border-radius:18px; border:1px solid #fecaca; background:#fef2f2; color:#7f1d1d;}
        .metric-help {font-size:.84rem; color: var(--stego-muted);}
        .backend-status-box {
            background-color: #0F2419;
            color: #7CFFB2;
            border: 1px solid #1E5A3C;
            border-radius: 12px;
            padding: 14px 16px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .backend-status-error {
            background-color: #2A1113;
            color: #FFB4B4;
            border: 1px solid #7A1F28;
            border-radius: 12px;
            padding: 14px 16px;
            font-weight: 600;
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.12);
        }
        div[data-testid="stButton"] > button {border-radius: 12px; font-weight: 700;}
        div[data-testid="stDownloadButton"] > button {border-radius: 12px; font-weight: 700;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, session_id: str | None = None) -> None:
    st.title(title)
    st.caption(subtitle)
    if session_id:
        with st.expander("Session information", expanded=False):
            st.code(session_id)


def render_sidebar_status(health_func, error_cls) -> None:
    with st.sidebar:
        st.markdown("### Backend Status")
        try:
            status = health_func()
            st.markdown(
                f"""
                <div class="backend-status-box">
                    <strong>Status:</strong> {html.escape(status['status'])}
                </div>
                """,
                unsafe_allow_html=True
            )

        except error_cls as exc:
            st.markdown(
                f"""
                <div class="backend-status-error">
                    <strong>Error:</strong> {html.escape(str(exc))}
                </div>
                """,
                unsafe_allow_html=True
            )
        st.divider()
        st.caption(
            "Tip: Use Encode first, then decode the generated image or retrieval code.")
        st.divider()


def estimate_payload_capacity(image_bytes: bytes | None, secret_text: str) -> None:
    if not image_bytes:
        st.caption("Upload an image to estimate capacity.")
        return
    approx_capacity_chars = max(1, len(image_bytes) // 8)
    used = len(secret_text.encode("utf-8"))
    pct = min(100, int((used / approx_capacity_chars) * 100))
    st.progress(pct / 100, text=f"Approx. capacity used: {pct}%")
    st.caption("Capacity is estimated from file size. Actual capacity depends on image dimensions and selected method.")
