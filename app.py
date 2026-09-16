import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="LocaPulse AI - SMB Visibility Engine",
    page_icon="⚡",
    layout="wide"
)

# Mengambil konfigurasi dari secrets Streamlit Cloud atau Environment
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
project_id = st.secrets.get("GCP_PROJECT_ID", os.environ.get("GCP_PROJECT_ID"))
location = st.secrets.get("GCP_LOCATION", "global")

if not api_key:
    st.error("API Key belum terpasang! Silakan tambahkan GEMINI_API_KEY di menu Secrets Streamlit.")
    st.stop()

# Inisialisasi client resmi Vertex AI
client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
    api_key=api_key
)

st.title("⚡ LocaPulse AI: Local Visibility & Web Engine")
st.caption("Engine otomatisasi audit profil bisnis fisik, SEO teknis, microsite instan, dan evaluasi kepatuhan pedoman lokal.")

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

    with st.status("Sedang menjalankan pipeline 4-Agent AI...", expanded=True) as status:
        
        try:
            # 1. AGENT 1: LOCAL PROFILE & GBP STRATEGIST
            st.write("🔍 Agent 1: Menganalisis visibilitas & profil Google Business...")
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

            # 2. AGENT 2: TECHNICAL SEO & LOCAL SCHEMA SPECIALIST
            st.write("⚙️ Agent 2: Mengompilasi Schema Markup JSON-LD & On-Page Meta...")
            prompt_seo = f"""
            Peran: Senior Technical SEO & Local Schema Specialist.
            Buatkan konfigurasi optimasi teknis on-page dan metadata untuk bisnis berikut:
            - Nama Bisnis: {business_name}
            - Kategori: {business_niche}
            - Wilayah: {business_city}
            - Kontak WA: {phone_number}
            - Info Tambahan: {additional_notes}

            Tugas:
            1. Buat kode Schema JSON-LD bertipe `LocalBusiness` lengkap (name, description, telephone, address, areaServed).
            2. Tuliskan tag meta penting: Title tag SEO (< 60 karakter), Meta Description (< 160 karakter), dan Open Graph tags (og:title, og:description).
            3. Berikan 3 rekomendasi NAP (Name, Address, Phone) consistency checklist untuk platform direktori lokal.

            Format Output: Markdown rapi, dengan blok kode ```json untuk Schema dan ```html untuk tag meta.
            """

            res_seo = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_seo,
            )
            seo_output = res_seo.text

            # 3. AGENT 3: FRONTEND WEB DEVELOPER
            st.write("💻 Agent 3: Mengompilasi kode HTML single-page dengan Tailwind CSS...")
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

            # 4. AGENT 4: QUALITY ASSURANCE & POLICY COMPLIANCE SPECIALIST
            st.write("🛡️ Agent 4: Menguji kepatuhan kebijakan Google, validasi NAP, & performa...")
            prompt_qa = f"""
            Peran: Lead Quality Assurance & Google Policy Compliance Specialist.
            Tugas: Lakukan audit kepatuhan dan validasi teknis terhadap hasil audit GBP dan strategi SEO berikut.

            Data Input Bisnis:
            - Nama Bisnis: {business_name}
            - Kategori: {business_niche}
            - Kota: {business_city}
            - No WA: {phone_number}

            Hasil Audit GBP & Deskripsi:
            {audit_output}

            Hasil Schema & Meta Tags:
            {seo_output}

            Kriteria Pengujian:
            1. **Google Business Profile Policy Check**: Periksa apakah ada pelanggaran (keyword stuffing di nama bisnis, klaim berlebihan, karakter terlarang, atau risiko penangguhan profil).
            2. **NAP & Schema Integrity**: Cek konsistensi format nomor telepon, penulisan lokasi, dan struktur Schema JSON-LD.
            3. **UX & Conversion Readiness**: Evaluasi kejelasan Call-to-Action (CTA) dan kenyamanan pembaca di perangkat seluler.
            4. **Skor Kesiapan & Rekomendasi Perbaikan**: Berikan skor (0-100%) dan poin tindakan prioritas sebelum materi dipublikasikan.

            Format Output: Markdown terstruktur dengan status badge (Contoh: [PASS], [WARNING], [ACTION NEEDED]).
            """

            res_qa = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_qa,
            )
            qa_output = res_qa.text

            status.update(label="Seluruh Pipeline Multi-Agent Selesai!", state="complete", expanded=False)

            # Panel Kiri: 3 Tab Hasil Analisis & QA
            with col_left:
                tab_gbp, tab_seo, tab_qa = st.tabs(["📋 Audit GBP", "🎯 SEO & Schema", "🛡️ QA & Kepatuhan"])
                with tab_gbp:
                    st.markdown(audit_output)
                with tab_seo:
                    st.markdown(seo_output)
                with tab_qa:
                    st.markdown(qa_output)

            # Panel Kanan: Live Preview & File Download
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
