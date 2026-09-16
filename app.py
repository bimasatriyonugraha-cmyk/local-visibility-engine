import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="LocaPulse AI - SMB Visibility Engine",
    page_icon="⚡",
    layout="wide"
)

# Mengambil konfigurasi dari secrets Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
project_id = st.secrets.get("GCP_PROJECT_ID", os.environ.get("GCP_PROJECT_ID"))
location = st.secrets.get("GCP_LOCATION", "global")

if not api_key:
    st.error("API Key belum terpasang! Silakan tambahkan GEMINI_API_KEY di menu Secrets Streamlit.")
    st.stop()

# Inisialisasi client Vertex AI resmi (memotong kredit Google Cloud)
client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
    api_key=api_key
)

st.title("⚡ LocaPulse AI: Local Visibility & Web Engine")
st.caption("Engine otomatisasi audit profil bisnis fisik dan penerbitan microsite instan berbasis AI.")

# Sidebar: Form Input
with st.sidebar:
    st.header("Data Usaha Klien")
    business_name = st.text_input("Nama Usaha UMKM", placeholder="Contoh: Defa Digi")
    business_niche = st.text_input("Kategori / Niche", placeholder="Contoh: Konsultan Google Business Profile")
    business_city = st.text_input("Kota / Wilayah", placeholder="Contoh: Semarang, Jawa Tengah")
    phone_number = st.text_input("Nomor WhatsApp", placeholder="Contoh: 6281234567890")
    additional_notes = st.text_area(
        "Konteks & Keunggulan",
        placeholder="Contoh: Spesialis merawat GBP biar sehat dan pembuatan microsite instan."
    )
    
    run_btn = st.button("Jalankan Pipeline AI", type="primary", use_container_width=True)

col_left, col_right = st.columns([1, 1])

if run_btn and business_name:
    slug = business_name.lower().replace(" ", "-").replace(".", "")

    with st.status("Sedang memproses riset dan generate website...", expanded=True) as status:
        
        try:
            # 1. LOCAL SEO & GBP AUDIT
            st.write("🔍 Menganalisis visibilitas & profil bisnis lokal...")
            prompt_audit = f"""
            Peran: Senior Local SEO Auditor & Google Business Profile Specialist.
            Analisis profil bisnis berikut:
            - Nama Bisnis: {business_name}
            - Kategori: {business_niche}
            - Wilayah: {business_city}
            - Info Tambahan: {additional_notes}

            Tugas:
            1. Berikan 5 targeted local keywords relevan.
            2. Tulis deskripsi profil Google Business Profile baru (maksimal 750 karakter) yang ramah SEO dan persuasif.
            3. Buat 2 ide postingan penawaran / update mingguan.
            4. Susun 1 template sapaan penawaran via WhatsApp ke pemilik bisnis.

            Output: Format Markdown yang rapi dan profesional.
            """
            
            res_audit = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_audit,
            )
            audit_output = res_audit.text

            # 2. GENERATE LANDING PAGE (TAILWIND CSS)
            st.write("💻 Mengompilasi kode HTML single-page dengan Tailwind CSS...")
            prompt_web = f"""
            Peran: Senior Frontend Developer.
            Buatkan 1 file HTML utuh (single-page) mandiri tanpa file eksternal selain Tailwind CDN untuk:
            - Nama Usaha: {business_name}
            - Bidang/Kategori: {business_niche} di {business_city}
            - Nomor Kontak WA: {phone_number}
            - Keunggulan: {additional_notes}

            Spesifikasi Desain & Teknis:
            1. Pasang Tailwind CSS CDN (<script src="https://cdn.tailwindcss.com"></script>).
            2. Gunakan font clean 'Plus Jakarta Sans'.
            3. Mobile-first responsive (terlihat rapi di HP maupun desktop).
            4. Komponen wajib:
               - Header dengan jam operasional & tombol kontak cepat.
               - Hero Section dengan judul memikat & tombol CTA WhatsApp langsung.
               - Grid Card daftar layanan / produk unggulan.
               - Testimoni pelanggan bintang 5.
               - Footer lengkap dengan alamat dan peta placeholder.
            5. Output HANYA kode HTML mentah, jangan sertakan tanda markdown ```html atau ```.
            """

            res_web = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_web,
            )
            
            raw_text = res_web.text or ""
            html_code = raw_text.replace("```html", "").replace("```", "").strip()
            status.update(label="Website & Laporan Berhasil Dibuat!", state="complete", expanded=False)

            with col_left:
                st.subheader("📋 Audit & Strategi Profil")
                st.markdown(audit_output)

            with col_right:
                st.subheader("🌐 Pratinjau Halaman Web")
                st.components.v1.html(html_code, height=600, scrolling=True)
                st.download_button(
                    label="⬇️ Download File index.html",
                    data=html_code,
                    file_name=f"{slug}-index.html",
                    mime="text/html",
                    use_container_width=True
                )

        except Exception as e:
            status.update(label="Terjadi Kesalahan", state="error", expanded=True)
            st.error(f"Pesan error sistem: {e}")

else:
    with col_left:
        st.info("Isi data bisnis di panel sebelah kiri lalu klik tombol **Jalankan Pipeline AI**.")
    with col_right:
        st.empty()
