import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="LocaPulse AI - SMB Visibility Engine",
    page_icon="⚡",
    layout="wide"
)

# Inisialisasi Session State untuk alur Human-in-the-Loop
if "pipeline_data" not in st.session_state:
    st.session_state.pipeline_data = None
if "is_refined" not in st.session_state:
    st.session_state.is_refined = False

# Konfigurasi Secrets Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
project_id = st.secrets.get("GCP_PROJECT_ID", os.environ.get("GCP_PROJECT_ID"))
location = st.secrets.get("GCP_LOCATION", "global")

if not api_key:
    st.error("API Key belum terpasang! Silakan tambahkan GEMINI_API_KEY di menu Secrets Streamlit.")
    st.stop()

# Inisialisasi client Vertex AI
client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
    api_key=api_key
)

st.title("⚡ LocaPulse AI: Local Visibility & Web Engine")
st.caption("Human-in-the-Loop Multi-Agent: Audit GBP, Schema SEO, QA Review, & Refinement Interaktif.")

# Sidebar: Form Input Bisnis
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
    
    run_btn = st.button("🚀 1. Jalankan Analisis Awal", type="primary", use_container_width=True)

# ----------------- PIPELINE TAHAP 1: DRAF AWAL & QA REVIEW -----------------
if run_btn and business_name:
    st.session_state.is_refined = False
    slug = business_name.lower().replace(" ", "-").replace(".", "")

    with st.status("Sedang memproses tahap awal multi-agent...", expanded=True) as status:
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
            raw_audit = res_audit.text

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
            2. Tuliskan tag meta penting: Title tag SEO (< 60 karakter), Meta Description (< 160 karakter), dan Open Graph tags.
            3. Berikan 3 rekomendasi NAP consistency checklist untuk direktori lokal.

            Format Output: Markdown rapi dengan blok kode ```json dan ```html.
            """
            res_seo = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_seo,
            )
            raw_seo = res_seo.text

            # 3. AGENT 3: QUALITY ASSURANCE (CRITIC AGENT)
            st.write("🛡️ Agent 3: Melakukan evaluasi kepatuhan pedoman & integritas data...")
            prompt_qa = f"""
            Peran: Lead Quality Assurance & Google Policy Auditor.
            Lakukan evaluasi kritis terhadap hasil draf GBP dan SEO berikut:

            Data Bisnis Asli:
            - Nama: {business_name} | Kategori: {business_niche} | Kota: {business_city} | WA: {phone_number}

            Draf GBP:
            {raw_audit}

            Draf SEO & Schema:
            {raw_seo}

            Kriteria Penilaian:
            1. Deteksi kata-kata berlebihan, spam, atau potensi pelanggaran pedoman Google Business Profile.
            2. Konsistensi penulisan NAP (Name, Address, Phone).
            3. Batasan karakter title (<60 char) dan deskripsi (<160 char).
            4. Tuliskan ringkasan poin perbaikan yang direkomendasikan.

            Output: Format Markdown dengan badge [PASS], [WARNING], atau [FIX NEEDED].
            """
            res_qa = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_qa,
            )
            qa_notes = res_qa.text

            # 4. AGENT 4: FRONTEND WEB DUMMY INITIAL
            st.write("💻 Agent 4: Mengompilasi Landing Page draf dengan foto dummy...")
            prompt_web = f"""
            Peran: Senior Frontend Developer.
            Buatkan 1 file HTML utuh mandiri (Tailwind CSS CDN) untuk:
            - Nama Usaha: {business_name}
            - Bidang/Kategori: {business_niche} di {business_city}
            - Kontak WA: {phone_number}
            - Konteks: {additional_notes}

            Placeholder Foto:
            - Hero: https://picsum.photos/seed/{slug}-hero/1200/600 (Tambahkan komentar: <!-- GANTI URL FOTO HERO DISINI -->)
            - Layanan 1: https://picsum.photos/seed/{slug}-srv1/600/400 (Tambahkan komentar: <!-- GANTI URL FOTO LAYANAN DISINI -->)
            - Layanan 2: https://picsum.photos/seed/{slug}-srv2/600/400 (Tambahkan komentar: <!-- GANTI URL FOTO LAYANAN DISINI -->)
            - Layanan 3: https://picsum.photos/seed/{slug}-srv3/600/400 (Tambahkan komentar: <!-- GANTI URL FOTO LAYANAN DISINI -->)
            - Komponen: Header, Hero + CTA WhatsApp, Grid Layanan, Testimoni, Footer.
            Output HANYA kode HTML mentah (tanpa ```html).
            """
            res_web = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_web,
            )
            raw_text = res_web.text or ""
            html_code = raw_text.replace("```html", "").replace("```", "").strip()

            # Simpan hasil ke Session State
            st.session_state.pipeline_data = {
                "business_name": business_name,
                "business_niche": business_niche,
                "business_city": business_city,
                "phone_number": phone_number,
                "additional_notes": additional_notes,
                "slug": slug,
                "audit": raw_audit,
                "seo": raw_seo,
                "qa_notes": qa_notes,
                "html_code": html_code,
            }
            status.update(label="Tahap Analisis Selesai! Silakan cek tab QA Review.", state="complete", expanded=False)

        except Exception as e:
            status.update(label="Terjadi Kesalahan", state="error", expanded=True)
            st.error(f"Pesan error sistem: {e}")

# ----------------- TAMPILAN INTERAKTIF & HUMAN-IN-THE-LOOP -----------------
if st.session_state.pipeline_data:
    data = st.session_state.pipeline_data
    col_left, col_right = st.columns([1, 1])

    with col_left:
        tab_audit, tab_seo, tab_qa = st.tabs(["📋 Draf GBP & Copy", "🎯 SEO & Schema", "🛡️ QA Review & Human Action"])
        
        with tab_audit:
            st.markdown(data["audit"])
            
        with tab_seo:
            st.markdown(data["seo"])
            
        with tab_qa:
            st.subheader("Catatan Audit QA Agent")
            st.markdown(data["qa_notes"])
            
            st.divider()
            st.markdown("### ✍️ Human-in-the-Loop: Terapkan Perbaikan")
            st.caption("Kamu bisa menambahkan instruksi tambahan ke AI sebelum menyetujui hasil revisi:")
            
            user_feedback = st.text_input(
                "Catatan Tambahan (Opsional):", 
                placeholder="Contoh: Tolong buatkan gaya bahasa lebih santai dan fokuskan kata kunci di Gunungpati."
            )
            
            apply_btn = st.button("✨ Terapkan Hasil QA & Perbaiki Otomatis (Apply Fixes)", type="primary")

            if apply_btn:
                with st.spinner("Sedang memoles output, mengompilasi web, dan menjalankan QA Re-Audit..."):
                    try:
                        # 1. PROSES REVISI STRATEGI
                        prompt_refine = f"""
                        Peran: Master Local SEO Polisher.
                        Tulis ulang strategi GBP dan SEO berikut dengan menerapkan SEMUA catatan tim QA serta feedback pengguna.

                        Draf Awal:
                        {data['audit']}
                        {data['seo']}

                        Catatan QA Awal:
                        {data['qa_notes']}

                        Instruksi Tambahan Pengguna:
                        {user_feedback if user_feedback else 'Terapkan semua saran QA tanpa tambahan lain.'}

                        Output: Markdown terstruktur dengan format rapi (Bagian GBP Final & Bagian Schema SEO Final).
                        """
                        res_refine = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt_refine,
                        )
                        refined_strategy = res_refine.text

                        # 2. QA AGENT ROUND 2: RE-AUDIT HASIL REVISI
                        prompt_re_qa = f"""
                        Peran: Lead Quality Assurance & Google Policy Compliance Auditor.
                        Tugas: Lakukan Re-Audit putaran kedua terhadap hasil revisi akhir berikut:

                        Hasil Strategi yang Sudah Direvisi:
                        {refined_strategy}

                        Kriteria:
                        1. Verifikasi apakah catatan kritik sebelumnya sudah terselesaikan dengan baik.
                        2. Pastikan tidak ada pelanggaran baru pada pedoman Google Business Profile atau sintaks schema.
                        3. Berikan skor akhir kesiapan (0-100%) dan pernyataan kelayakan publikasi: [100% PASS - READY TO PUBLISH].
                        """
                        res_re_qa = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt_re_qa,
                        )
                        re_qa_notes = res_re_qa.text

                        # 3. REKOMPILASI WEB DENGAN DATA YANG SUDAH TERVALIDASI
                        prompt_web_refined = f"""
                        Peran: Senior Frontend Developer.
                        Perbarui kode landing page HTML (Tailwind CSS) dengan konten yang sudah disempurnakan:
                        - Nama Usaha: {data['business_name']}
                        - Wilayah: {data['business_city']}
                        - Kontak WA: {data['phone_number']}
                        - Konten Baru yang Sudah Disempurnakan:
                        {refined_strategy}

                        Placeholder Foto:
                        - Hero: [https://picsum.photos/seed/](https://picsum.photos/seed/){data['slug']}-hero/1200/600 (<!-- GANTI URL FOTO HERO DISINI -->)
                        - Layanan 1: [https://picsum.photos/seed/](https://picsum.photos/seed/){data['slug']}-srv1/600/400 (<!-- GANTI URL FOTO LAYANAN DISINI -->)
                        - Layanan 2: [https://picsum.photos/seed/](https://picsum.photos/seed/){data['slug']}-srv2/600/400 (<!-- GANTI URL FOTO LAYANAN DISINI -->)
                        - Layanan 3: [https://picsum.photos/seed/](https://picsum.photos/seed/){data['slug']}-srv3/600/400 (<!-- GANTI URL FOTO LAYANAN DISINI -->)

                        Output HANYA kode HTML mentah (tanpa ```html).
                        """
                        res_web_refine = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt_web_refined,
                        )
                        raw_web_refine = res_web_refine.text or ""
                        new_html = raw_web_refine.replace("```html", "").replace("```", "").strip()

                        # Update data di session state termasuk laporan QA putaran kedua
                        data["audit"] = refined_strategy
                        data["qa_notes"] = f"### 🛡️ HASIL RE-AUDIT QA PUTARAN KEDUA (PASCA REVISI)\n\n{re_qa_notes}\n\n---\n\n### 📜 Arsip Audit Draf Awal:\n{data['qa_notes']}"
                        data["html_code"] = new_html
                        st.session_state.is_refined = True
                        st.success("✅ Output, Halaman Web, dan Re-Audit QA berhasil diperbarui!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Gagal melakukan perbaikan: {e}")

    # Panel Kanan: Web Live Preview & Download
    with col_right:
        if st.session_state.is_refined:
            st.success("🌟 Menampilkan Pratinjau Web yang Telah Direvisi (Final)")
        else:
            st.info("ℹ️ Menampilkan Pratinjau Draf Awal (Belum diapply perbaikan QA)")
            
        st.subheader("🌐 Pratinjau Halaman Web")
        st.components.v1.html(data["html_code"], height=650, scrolling=True)
        st.download_button(
            label="⬇️ Download File index.html",
            data=data["html_code"],
            file_name=f"{data['slug']}-index.html",
            mime="text/html",
            use_container_width=True
        )

else:
    st.info("👈 Masukkan data usaha di sidebar sebelah kiri lalu klik tombol **🚀 1. Jalankan Analisis Awal**.")
