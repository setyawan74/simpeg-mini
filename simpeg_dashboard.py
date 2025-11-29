import streamlit as st
import pandas as pd
import bcrypt
from datetime import date
from io import BytesIO

# ================== Inisialisasi Data ==================
EXPECTED_COLS = [
    "NAMA","NIP","GELAR DEPAN","GELAR BELAKANG","TEMPAT LAHIR","TANGGAL LAHIR",
    "JENIS KELAMIN","AGAMA","JENIS KAWIN","NIK","NOMOR HP","EMAIL","ALAMAT",
    "NPWP","BPJS","JENIS PEGAWAI","KEDUDUKAN HUKUM","STATUS CPNS PNS",
    "KARTU ASN VIRTUAL","TMT CPNS","TMT PNS","GOL AWAL","GOL AKHIR",
    "TMT GOLONGAN","MK TAHUN","MK BULAN","JENIS JABATAN","NAMA JABATAN",
    "TMT JABATAN","TINGKAT PENDIDIKAN","NAMA PENDIDIKAN","NAMA UNOR","UNOR INDUK"
]

if "pegawai" not in st.session_state:
    st.session_state.pegawai = pd.DataFrame(columns=EXPECTED_COLS)

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {
            "password_hash": bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "role": "Admin"
        }
    }

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

# ================== Auth helpers ==================
def login(username, password):
    if username in st.session_state.users:
        info = st.session_state.users[username]
        if bcrypt.checkpw(password.encode("utf-8"), info["password_hash"].encode("utf-8")):
            st.session_state.auth = {"logged_in": True, "username": username, "role": info["role"]}
            return True
    return False

def logout():
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

def is_admin():
    return st.session_state.auth["role"] == "Admin"

def is_supervisor():
    return st.session_state.auth["role"] == "Supervisor"

# ================== CSS ==================
st.markdown("""
    <style>
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        text-align: center;
        width: 100%;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: white;
    }
    .card h4 { margin: 0; font-size: 16px; font-weight: bold; }
    .card h2 { margin: 5px 0 0 0; font-size: 28px; }
    </style>
""", unsafe_allow_html=True)

# ================== Header ==================
st.markdown('<h1 style="text-align:center;">SISTEM INFORMASI KEPEGAWAIAN</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;color:gray;">Halaman Admin/User/Supervisor</h3>', unsafe_allow_html=True)

# ================== Login ==================
if not st.session_state.auth["logged_in"]:
    st.sidebar.title("Login")
    with st.sidebar.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Masuk")
    if submit_login:
        if login(user, pw):
            st.success(f"Login berhasil! Selamat datang, {user}.")
        else:
            st.error("Login gagal. Periksa username/password.")
    st.stop()

# ================== Sidebar ==================
st.sidebar.title("PANEL")
menu = st.sidebar.radio(
    "Navigasi",
    ["Dashboard", "Pegawai", "Pegawai Grafik", "Laporan", "Rekapitulasi", "Backup/Hapus Data"]
)
st.sidebar.write(f"Login sebagai: {st.session_state.auth['username']} ({st.session_state.auth['role']})")
if st.sidebar.button("Logout"):
    logout()
    st.stop()

# ================== Dashboard ==================
if menu == "Dashboard":
    df = st.session_state.pegawai
    total = len(df)
    user_count = len(st.session_state.users)

    if "JENIS KELAMIN" in df.columns and not df.empty:
        jk = df["JENIS KELAMIN"].astype(str).str.strip().str.upper()
        laki = jk.isin(["M","LAKI-LAKI","L","PRIA"]).sum()
        perempuan = jk.isin(["F","PEREMPUAN","P","WANITA"]).sum()
    else:
        laki, perempuan = 0, 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="card" style="background:#2196f3;">👨<br><h4>LAKI-LAKI</h4><h2>{laki}</h2></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="card" style="background:#e91e63;">👩<br><h4>PEREMPUAN</h4><h2>{perempuan}</h2></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="card" style="background:#9c27b0;">🔑<br><h4>USER</h4><h2>{user_count}</h2></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="card" style="background:#4caf50;">👥<br><h4>PEGAWAI</h4><h2>{total}</h2></div>', unsafe_allow_html=True)

    if is_admin():
        st.markdown("---")
        st.subheader("➕ Tambah pengguna")
        with st.form("add_user_form"):
            u = st.text_input("Username baru")
            p = st.text_input("Password baru", type="password")
            r = st.selectbox("Role", ["Admin", "User", "Supervisor"])
            submit_u = st.form_submit_button("Tambah")
        if submit_u and u and p:
            if u in st.session_state.users:
                st.warning("Username sudah ada.")
            else:
                st.session_state.users[u] = {
                    "password_hash": bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                    "role": r
                }
                st.success(f"Pengguna {u} ({r}) berhasil ditambahkan!")
        st.dataframe(pd.DataFrame([{"Username": uname, "Role": info["role"]} for uname, info in st.session_state.users.items()]), use_container_width=True)

# ================== Pegawai ==================
elif menu == "Pegawai":
    st.header("Data Pegawai")
    df = st.session_state.pegawai
    st.dataframe(df, use_container_width=True)

    if is_admin():
        st.subheader("Upload data pegawai (CSV/Excel)")
        uploaded_file = st.file_uploader("Pilih file", type=["csv", "xlsx"])
        if uploaded_file:
            df_new = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df_new.columns = [str(c).strip().upper() for c in df_new.columns]
            if all(col in df_new.columns for col in EXPECTED_COLS):
                st.session_state.pegawai = df_new
                st.success("Data pegawai berhasil diimpor!")
            else:
                st.error("Kolom file tidak sesuai. Harus ada semua header berikut:")
                st.write(EXPECTED_COLS)

        st.download_button(
            label="Unduh template CSV (header standar)",
            data=",".join(EXPECTED_COLS) + "\n",
            file_name="template_simpeg.csv",
            mime="text/csv"
        )

        st.subheader("Tambah pegawai baru")
        with st.form("tambah_pegawai"):
            nama = st.text_input("NAMA")
            nip = st.text_input("NIP")
            jabatan = st.text_input("NAMA JABATAN")
            nama_unor = st.text_input("NAMA UNOR")
            unor_induk = st.text_input("UNOR INDUK")
            tmt_jabatan = st.date_input("TMT JABATAN")
            submit = st.form_submit_button("Tambah")
        if submit and nama and nip:
            new_row = {col: "" for col in EXPECTED_COLS}
            new_row.update({
                "NAMA": nama,
                "NIP": nip,
                "NAMA JABATAN": jabatan,
                "NAMA UNOR": nama_unor,
                "UNOR INDUK": unor_induk,
                "TMT JABATAN": str(tmt_jabatan),
            })
            st.session_state.pegawai.loc[len(st.session_state.pegawai)] = new_row
            st.success("Pegawai ditambahkan!")

        st.subheader("Edit / Hapus Pegawai")
        nip_search = st.text_input("Masukkan NIP pegawai untuk edit/hapus")
        if nip_search:
            df_match = st.session_state.pegawai[st.session_state.pegawai["NIP"].astype(str) == str(nip_search)]
            if not df_match.empty:
                st.dataframe(df_match, use_container_width=True)
                idx = df_match.index[0]

                def default_tmt_value(val):
                    try:
                        return pd.to_datetime(val).date()
                    except Exception:
                        return date.today()

                with st.form("edit_pegawai"):
                    nama_edit = st.text_input("NAMA", value=str(df_match.iloc[0].get("NAMA", "")))
                    jabatan_edit = st.text_input("NAMA JABATAN", value=str(df_match.iloc[0].get("NAMA JABATAN", "")))
                    nama_unor_edit = st.text_input("NAMA UNOR", value=str(df_match.iloc[0].get("NAMA UNOR", "")))
                    unor_induk_edit = st.text_input("UNOR INDUK", value=str(df_match.iloc[0].get("UNOR INDUK", "")))
                    tmt_raw = df_match.iloc[0].get("TMT JABATAN", "")
                    tmt_edit = st.date_input("TMT JABATAN", value=default_tmt_value(tmt_raw))
                    submit_edit = st.form_submit_button("Simpan Perubahan")

                if submit_edit:
                    st.session_state.pegawai.at[idx, "NAMA"] = nama_edit
                    st.session_state.pegawai.at[idx, "NAMA JABATAN"] = jabatan_edit
                    st.session_state.pegawai.at[idx, "NAMA UNOR"] = nama_unor_edit
                    st.session_state.pegawai.at[idx, "UNOR INDUK"] = unor_induk_edit
                    st.session_state.pegawai.at[idx, "TMT JABATAN"] = str(tmt_edit)
                    st.success("Data pegawai berhasil diperbarui!")

                if st.button("Hapus Pegawai"):
                    st.session_state.pegawai = st.session_state.pegawai.drop(df_match.index).reset_index(drop=True)
                    st.success("Pegawai berhasil dihapus!")
            else:
                st.warning("Pegawai dengan NIP tersebut tidak ditemukan.")
    elif is_supervisor():
        st.info("Anda login sebagai Supervisor. Hanya bisa melihat data pegawai.")
    else:
        st.info("Anda login sebagai User. Hanya bisa melihat data pegawai.")

# ================== Pegawai Grafik ==================
elif menu == "Pegawai Grafik":
    st.header("Grafik Pegawai")
    df = st.session_state.pegawai

    # 1) Gender (bar chart)
    st.subheader("Distribusi berdasarkan jenis kelamin")
    if not df.empty and "JENIS KELAMIN" in df.columns:
        jk_series = df["JENIS KELAMIN"].astype(str).str.strip().str.upper()
        label_map = {
            "M":"LAKI-LAKI","L":"LAKI-LAKI","PRIA":"LAKI-LAKI","LAKI-LAKI":"LAKI-LAKI",
            "F":"PEREMPUAN","P":"PEREMPUAN","WANITA":"PEREMPUAN","PEREMPUAN":"PEREMPUAN"
        }
        jk_mapped = jk_series.map(lambda x: label_map.get(x, x))
        st.bar_chart(jk_mapped.value_counts())
    else:
        st.info("Data pegawai atau kolom JENIS KELAMIN belum tersedia.")

    # 2) Usia (bar chart per rentang)
    st.subheader("Distribusi berdasarkan usia (rentang)")
    if not df.empty and "TANGGAL LAHIR" in df.columns:
        df_age = df.copy()
        df_age["TANGGAL LAHIR"] = pd.to_datetime(df_age["TANGGAL LAHIR"], errors="coerce")
        df_age["USIA"] = df_age["TANGGAL LAHIR"].apply(lambda x: (pd.Timestamp.today().year - x.year) if pd.notnull(x) else None)
        usia_series = df_age["USIA"].dropna().astype(int)
        if not usia_series.empty:
            bins = [0, 20, 30, 40, 50, 60, 150]
            labels = ["<20", "20–29", "30–39", "40–49", "50–59", "60+"]
            usia_bucket = pd.cut(usia_series, bins=bins, labels=labels, right=False, include_lowest=True)
            usia_counts = usia_bucket.value_counts().reindex(labels).fillna(0).astype(int)
            st.bar_chart(usia_counts)
        else:
            st.info("Data usia pegawai tidak tersedia atau tidak valid.")
    else:
        st.info("Kolom TANGGAL LAHIR belum tersedia.")

    # 3) Tingkat pendidikan (bar chart dengan kamus normalisasi diperluas + fallback)
    st.subheader("Distribusi berdasarkan tingkat pendidikan")
    if not df.empty and "TINGKAT PENDIDIKAN" in df.columns:
        pend_series = df["TINGKAT PENDIDIKAN"].astype(str).str.strip().str.upper()
        norm_map = {
            # Pendidikan dasar
            "SD":"SD","SEKOLAH DASAR":"SD","ELEMENTARY SCHOOL":"SD",
            "SMP":"SMP","SEKOLAH MENENGAH PERTAMA":"SMP","JUNIOR HIGH":"SMP",
            # Menengah
            "SMA":"SMA","SMU":"SMA","SMK":"SMA","MA":"SMA","SEKOLAH MENENGAH ATAS":"SMA","HIGH SCHOOL":"SMA",
            # Diploma
            "D1":"D1","DIPLOMA I":"D1",
            "D2":"D2","DIPLOMA II":"D2",
            "D3":"D3","DIPLOMA III":"D3","AHLI MADYA":"D3",
            "D4":"D4","DIPLOMA IV":"D4","SARJANA TERAPAN":"D4",
            # Sarjana
            "S1":"S1","SARJANA":"S1","SARJANA STRATA 1":"S1","UNDERGRADUATE":"S1","BACHELOR":"S1",
            # Magister
            "S2":"S2","MAGISTER":"S2","MASTER":"S2","MAGISTER MANAJEMEN":"S2","POSTGRADUATE":"S2",
            # Doktor
            "S3":"S3","DOKTOR":"S3","PHD":"S3","DOKTOR ILMU HUKUM":"S3","DOCTORATE":"S3"
        }
        pend_norm = pend_series.map(lambda x: norm_map.get(x, x))
        pend_counts = pend_norm.value_counts().sort_index()
        st.bar_chart(pend_counts)
    else:
        st.info("Kolom TINGKAT PENDIDIKAN belum tersedia.")

# ================== Laporan ==================
elif menu == "Laporan":
    st.header("Laporan Pegawai")
    df = st.session_state.pegawai
    if not df.empty:
        units = sorted([u for u in df["UNOR INDUK"].dropna().astype(str).str.strip().unique()]) if "UNOR INDUK" in df.columns else []
        unit_filter = st.selectbox("Pilih UNOR INDUK untuk laporan nominatif", ["Semua"] + units) if len(units) > 0 else "Semua"
        df_filtered = df.copy()
        if unit_filter != "Semua" and "UNOR INDUK" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["UNOR INDUK"].astype(str).str.strip() == unit_filter]

        # Grafik jumlah pegawai per UNOR INDUK
        if "UNOR INDUK" in df_filtered.columns:
            chart_df = df_filtered["UNOR INDUK"].astype(str).str.strip().value_counts().reset_index()
            chart_df.columns = ["UNOR INDUK", "JUMLAH"]
            st.subheader("Grafik jumlah pegawai per UNOR INDUK")
            st.bar_chart(chart_df.set_index("UNOR INDUK"))
        else:
            st.warning("Kolom UNOR INDUK tidak ditemukan.")

        st.markdown("---")

        # Rekap per Nama Jabatan
        if "NAMA JABATAN" in df_filtered.columns:
            nama_jabatan_df = df_filtered["NAMA JABATAN"].astype(str).str.strip().value_counts().reset_index()
            nama_jabatan_df.columns = ["NAMA JABATAN", "JUMLAH"]
            st.subheader("Rekap per Nama Jabatan" + (f" • {unit_filter}" if unit_filter != "Semua" else ""))
            st.dataframe(nama_jabatan_df, use_container_width=True)
            st.bar_chart(nama_jabatan_df.set_index("NAMA JABATAN"))
        else:
            st.warning("Kolom NAMA JABATAN tidak ditemukan.")

        st.markdown("---")

        # Rekap per Jenis Jabatan
        if "JENIS JABATAN" in df_filtered.columns:
            jenis_jabatan_df = df_filtered["JENIS JABATAN"].astype(str).str.strip().value_counts().reset_index()
            jenis_jabatan_df.columns = ["JENIS JABATAN", "JUMLAH"]
            st.subheader("Rekap per Jenis Jabatan" + (f" • {unit_filter}" if unit_filter != "Semua" else ""))
            st.dataframe(jenis_jabatan_df, use_container_width=True)
            st.bar_chart(jenis_jabatan_df.set_index("JENIS JABATAN"))
        else:
            st.warning("Kolom JENIS JABATAN tidak ditemukan.")

        st.markdown("---")

        # Nominatif per UNOR INDUK + Pencarian + Ekspor (Admin/Supervisor)
        if unit_filter != "Semua":
            st.subheader(f"Laporan Nominatif Pegawai • UNOR INDUK: {unit_filter}")
            search_term = st.text_input("Cari berdasarkan NIP atau Nama")
            df_nom = df_filtered.copy()
            if search_term:
                df_nom = df_nom[
                    df_nom["NIP"].astype(str).str.contains(search_term, case=False, na=False) |
                    df_nom["NAMA"].astype(str).str.contains(search_term, case=False, na=False)
                ]

            cols_show = ["NAMA","NIP","NAMA JABATAN","JENIS JABATAN","UNOR INDUK","NAMA UNOR","TMT JABATAN"]
            cols_show = [c for c in cols_show if c in df_nom.columns]
            st.dataframe(df_nom[cols_show], use_container_width=True)

            if not df_nom.empty:
                if is_admin() or is_supervisor():
                    out_xlsx = BytesIO()
                    with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as writer:
                        df_nom[cols_show].to_excel(writer, index=False, sheet_name="Nominatif")
                    xlsx_data = out_xlsx.getvalue()
                    st.download_button(
                        label="💾 Unduh Laporan Nominatif (Excel)",
                        data=xlsx_data,
                        file_name=f"nominatif_{unit_filter}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    csv_data = df_nom[cols_show].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="💾 Unduh Laporan Nominatif (CSV)",
                        data=csv_data,
                        file_name=f"nominatif_{unit_filter}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Ekspor laporan hanya tersedia untuk Admin/Supervisor.")
        else:
            st.info("Pilih UNOR INDUK untuk melihat dan ekspor laporan nominatif.")
    else:
        st.info("Belum ada data pegawai untuk ditampilkan.")

# ================== Rekapitulasi ==================
elif menu == "Rekapitulasi":
    st.header("Rekapitulasi Tren TMT JABATAN")
    df = st.session_state.pegawai
    if "TMT JABATAN" in df.columns and not df.empty:
        df_ts = df.copy()
        df_ts["TMT JABATAN"] = pd.to_datetime(df_ts["TMT JABATAN"], errors="coerce")
        df_ts = df_ts.dropna(subset=["TMT JABATAN"])
        if df_ts.empty:
            st.info("Tidak ada TMT JABATAN yang valid untuk direkap.")
        else:
            units = sorted([u for u in df_ts["UNOR INDUK"].dropna().astype(str).str.strip().unique()]) if "UNOR INDUK" in df_ts.columns else []
            unit_filter = st.selectbox("Filter UNOR INDUK (opsional)", ["Semua"] + units) if len(units) > 0 else "Semua"
            df_filtered = df_ts.copy()
            if unit_filter != "Semua" and "UNOR INDUK" in df_filtered.columns:
                df_filtered = df_filtered[df_filtered["UNOR INDUK"].astype(str).str.strip() == unit_filter]

            tahun_list = sorted(df_filtered["TMT JABATAN"].dt.year.unique())
            tahun = st.selectbox("Pilih Tahun", tahun_list) if len(tahun_list) > 0 else None

            if tahun is not None:
                df_year = df_filtered[df_filtered["TMT JABATAN"].dt.year == tahun]
                rekap_bulan = df_year.groupby(df_year["TMT JABATAN"].dt.month).size().reset_index(name="JUMLAH")
                rekap_bulan["BULAN"] = rekap_bulan["TMT JABATAN"].apply(lambda x: f"Bulan {x}")
                st.subheader(f"Tren Bulanan Tahun {tahun}" + (f" • UNOR INDUK: {unit_filter}" if unit_filter != "Semua" else ""))
                st.dataframe(rekap_bulan[["BULAN", "JUMLAH"]], use_container_width=True)
                st.line_chart(rekap_bulan.set_index("BULAN")["JUMLAH"])

                st.markdown("---")
                rekap_tahun = df_filtered.groupby(df_filtered["TMT JABATAN"].dt.year).size().reset_index(name="JUMLAH")
                rekap_tahun.columns = ["TAHUN", "JUMLAH"]
                st.subheader("Tren Tahunan" + (f" • UNOR INDUK: {unit_filter}" if unit_filter != "Semua" else ""))
                st.dataframe(rekap_tahun, use_container_width=True)
                st.line_chart(rekap_tahun.set_index("TAHUN")["JUMLAH"])
            else:
                st.info("Tidak ada tahun yang dapat dipilih pada data terfilter.")
    else:
        st.info("Kolom TMT JABATAN belum tersedia atau kosong.")

    # Indikator hak akses di Rekapitulasi
    if is_admin():
        st.success("Anda Admin: punya akses penuh termasuk Backup/Hapus Data.")
    elif is_supervisor():
        st.info("Anda Supervisor: bisa melihat tren, tanpa akses Backup/Hapus Data.")
    else:
        st.info("Anda User: hanya bisa melihat tren.")

# ================== Backup / Hapus Data ==================
elif menu == "Backup/Hapus Data":
    st.header("Backup & Hapus Data Pegawai")
    if is_admin():
        df = st.session_state.pegawai

        if not df.empty:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="💾 Backup Data Pegawai (CSV)",
                data=csv_data,
                file_name="backup_pegawai.csv",
                mime="text/csv"
            )
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Pegawai")
            excel_data = output.getvalue()
            st.download_button(
                label="💾 Backup Data Pegawai (Excel)",
                data=excel_data,
                file_name="backup_pegawai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Tidak ada data pegawai untuk dibackup.")

        st.markdown("---")
        st.warning("Aksi ini akan menghapus semua data pegawai dan tidak bisa dibatalkan.")
        confirm = st.checkbox("Saya paham dan ingin menghapus semua data.")
        if st.button("🗑️ Hapus Semua Data Pegawai", disabled=not confirm):
            st.session_state.pegawai = pd.DataFrame(columns=EXPECTED_COLS)
            st.success("Semua data pegawai berhasil dihapus!")
    else:
        st.warning("Menu ini hanya bisa diakses oleh Admin.")
