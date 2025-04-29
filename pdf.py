import re
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Paragraph

def create_pdf(title, cue_points, notes, summary, filename):
    # Inisialisasi canvas
    c = canvas.Canvas(filename, pagesize=letter)
    page_width, page_height = letter

    def y_coord(y):
        return page_height - y

    def create_paragraph(text, x, y, width, font_name, font_size, alignment=TA_LEFT):
        style = ParagraphStyle(
            'custom',
            fontName=font_name,
            fontSize=font_size,
            leading=font_size + 2,
            alignment=alignment,
        )
        paragraph = Paragraph(text, style)
        paragraph.wrapOn(c, width, page_height)
        paragraph.drawOn(c, x, y - paragraph.height)
        return paragraph.height

    def split_text_into_sentences(text, max_chars_per_part):
        # Pisahkan berdasarkan kalimat
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        parts = []
        current_part = ""
        for sentence in sentences:
            if len(current_part) + len(sentence) <= max_chars_per_part:
                current_part += sentence + " "
            else:
                parts.append(current_part.strip())
                current_part = sentence + " "
        if current_part:
            parts.append(current_part.strip())
        return parts

    def split_bullets_evenly(bullets, num_pages):
        bullets_per_page = ceil(len(bullets) / num_pages)
        return [bullets[i:i+bullets_per_page] for i in range(0, len(bullets), bullets_per_page)]

    # Persiapan data
    cue_points_list = cue_points.split('<br/>')
    
    # Notes dan Summary dipotong berdasarkan kalimat dengan batasan jumlah karakter kira-kira 2000-an
    notes_parts = split_text_into_sentences(notes, 2100)
    summary_parts = split_text_into_sentences(summary, 700)

    # Jumlah halaman berdasarkan panjang notes/summary
    total_pages = max(len(notes_parts), len(summary_parts))

    # Bagi rata cue points ke total_pages
    cue_points_pages = split_bullets_evenly(cue_points_list, total_pages)

    for page_idx in range(total_pages):
        if page_idx > 0:
            c.showPage()

        # Title
        create_paragraph(
            title,
            40,
            y_coord(23),
            532,
            "Helvetica-Bold",
            18
        )

        # Gambar kotak
        c.setLineWidth(1)
        
        # Kotak kiri
        c.line(40, y_coord(100), 40 + 156, y_coord(100))  # Top
        c.line(40 + 156, y_coord(100), 40 + 156, y_coord(100) - 526)  # Right
        c.line(40, y_coord(100) - 526, 40 + 156, y_coord(100) - 526)  # Bottom
        
        # Kotak kanan
        c.line(196, y_coord(100), 196 + 376, y_coord(100))  # Top
        c.line(196, y_coord(100), 196, y_coord(100) - 526)  # Left
        c.line(196, y_coord(100) - 526, 196 + 376, y_coord(100) - 526)  # Bottom

        # Summary (kalau ada di halaman ini)
        if page_idx < len(summary_parts):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y_coord(633) - 12, "Summary")
            create_paragraph(
                summary_parts[page_idx],
                40,
                y_coord(654),
                532,
                "Helvetica",
                12,
                TA_JUSTIFY
            )

        # Header Cue/Key Points
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_coord(79) - 12, "Cue/Key Points")

        # Header Notes
        c.setFont("Helvetica-Bold", 12)
        c.drawString(205, y_coord(79) - 12, "Notes")

        # Isi Cue/Key Points
        cue_points_text = '<br/>'.join(cue_points_pages[page_idx]) if page_idx < len(cue_points_pages) else ''
        create_paragraph(
            cue_points_text,
            41,
            y_coord(107),
            145,
            "Helvetica",
            12
        )

        # Isi Notes
        notes_text = notes_parts[page_idx] if page_idx < len(notes_parts) else ''
        create_paragraph(
            notes_text,
            206,
            y_coord(106),
            366,
            "Helvetica",
            12,
            TA_JUSTIFY
        )

    c.save()

# Contoh penggunaan
create_pdf(
    title="Apa Itu Machine Learning?",
    notes="Apa itu Machine Learning Machine learning adalah salah satu bagian dari artificial intelligence yang memungkinkan mesin belajar dari data atau pengalaman masa lalu (data historis) sehingga tidak perlu diprogram secara manual untuk melakukan seluruh pekerjaan. Dengan kemampuan belajar secara otomatis, sistem bisa secara bertahap terus belajar meningkatkan akurasinya. Dalam konteks yang lebih sederhana, metode machine learning mirip dengan cara belajar manusia. Misalnya, seorang anak kecil diajari membaca huruf. Jika diajarkan terus menerus, pola-pola huruf itu akan melekat dan diingat oleh sang anak. Anak bisa mengenali huruf karena sudah memiliki pengetahuan dari pengalaman yang diajarkan kepadanya. Hal yang membedakan pembelajaran manusia dan mesin adalah manusia belajar dari pengalaman masa lalu, sementara machine learning belajar dari data. Itu sebabnya data menjadi objek penting dalam membuat machine learning. Tanpa data, machine tidak mendapatkan pengetahuan apa pun yang bisa dipelajari. Tipe” Algoritma Machine Learning Supervised learning adalah jenis pembelajaran di mana scientist memberikan sampel data berlabel (labeled data) kepada mesin. Pemberian sampel data bertujuan untuk melatih sistem dalam mempelajari kumpulan data dan berakhir dengan menguji model machine learning yang telah terbentuk. Pengujian model dilakukan untuk memeriksa apakah output yang dihasilkan sudah tepat atau belum. Kumpulan data ini melatih algoritma machine learning mengklasifikasikan data atau memprediksi hasil secara akurat. Jika diibaratkan, supervised learning adalah metode belajar yang diawasi guru/pengajar. Dikarenakan sistem belajarnya tidak otodidak, guru bisa langsung mengoreksi jika ada kesalahan. Unsupervised learning adalah jenis machine learning yang memberikan pembelajaran kepada kumpulan data tidak berlabel (unlabeled data). Di sini, tidak ada kategori yang menjadi dasar algoritma machine learning untuk membuat hubungan antar model. Dikarenakan tidak ada aspek data yang diketahui, algoritma tidak bisa memandu dan mengawasi input data. Alhasil, output bisa benar atau salah. Algoritma bekerja dengan cara mengumpulkan, mendeteksi pola, meringkas, lalu mengelompokkan data. Hasil pengelompokan data tersebut melatih mesin untuk belajar secara mandiri dari data-data yang ada, termasuk pola tersembunyi dalam data, sehingga campur tangan menusia menjadi sangat minimal. Contoh dari unsupervised learning adalah filter untuk memprediksi usia seseorang melalui kamera smartphone. Aplikasi bisa menghasilkan angka yang salah ataupun benar ketika melakukan deteksi. Kelebihan Machine Learning Dirangkum dari berbagai sumber, berikut kelebihan machine learning: Otomatisasi Dengan bantuan machine learning, banyak pekerjaan mulai menerapkan otomatisasi tugas. Otomatisasi membuat waktu dan tenaga yang dikeluarkan lebih efektif sekaligus efisien. Misalnya, website memanfaatkan fitur chatbot untuk mengatasi permasalahan customer lebih cepat. Chatbot bisa tersedia selama 24 jam penuh untuk menanggapi pertanyaan pelanggan. Terus melakukan perbaikan Proses pembelajaran mesin tidak pernah berakhir. Mesin akan terus belajar menyesuaikan data-data yang dipelajari. Banyaknya inovasi dan penelitian memungkinkan machine learning menjadi teknologi yang semakin canggih di masa depan. Jangkauan aplikasi sangat luas Teknik machine learning memiliki jangkauan sangat luas. Artinya, teknologi ini bisa digunakan hampir di semua bidang, termasuk kedokteran, perbankan, transportasi, media, dan pendidikan. Jangkauan yang luas menciptakan banyak peluang kemudahan di bidang tersebut. Meningkatkan kualitas di berbagai bidang Teknologi machine learning memungkinkan kualitas pekerjaan meningkat. Dengan mengandalkan kecanggihan teknologi, wawasan/informasi yang dihasilkan semakin akurat. Contohnya, Facebook memiliki fitur Lookalike Audience untuk menargetkan orang-orang yang memiliki kemiripan dengan audience perusahaan berdasarkan segmentasi, seperti demografi, minat dan perilaku. Alih-alih menggali data secara manual, terbatas, dan tingkat akurasi belum bisa dipastikan, Facebook telah membantu merangkum data dari seluruh pengguna platform-nya. Mengidentifikasi pola dan tren dengan mudah Sebagai bagian dari kecerdasan buatan, machine learning memiliki kemampuan untuk mempelajari sekaligus mengidentifikasi pola dan tren. Sistem bekerja dengan cara mengenali pola untuk kemudian menemukan solusi dari masalah tertentu. Menghemat waktu dan energi Salah satu fungsi teknologi adalah menghemat waktu dan energi manusia. Teknologi machine learning hadir untuk melakukan fungsi tersebut. Mesin dapat secara otomatis menjalankan tugas tanpa banyak interupsi dan campur tangan manusia. Kekurangan Machine Learning Machine learning juga memiliki kekurangan, antara lain: Memerlukan biaya dan sumber daya besar Pengembangan machine learning memerlukan biaya dan sumber daya yang besar. Biaya yang perlu dikeluarkan di antaranya untuk mempekerjakan programmer, data scientist, dan membeli mesin khusus. Peluang kesalahan tinggi Algoritma dibuat oleh manusia. Bukan tidak mungkin dalam pembuatan algoritma terjadi kesalahan. Kesalahan kecil dalam algoritma mengakibatkan output pembelajaran yang salah. Untuk itu, diperlukan ketelitian ekstra agar margin kesalahan bisa mencapai nol (tidak ada kesalahan sama sekali). Kualitas output data yang sangat tergantung input Pembelajaran mesin bergantung besar pada data dan algoritma. Jika terjadi kesalahan di salah satu faktor, dampaknya bisa sangat besar. Kualitas data yang di-input dalam mesin berpengaruh secara signifikan terhadap hasil yang dikeluarkan. Ketika sumber datanya salah, hasilnya tidak akan kredibel. Oleh sebab itu, data yang dikumpulkan tidak bisa sembarangan. Setiap ada ketidakcocokan dalam data apa pun, seluruh sistem menjadi tidak akurat. Spesialisasi untuk setiap project Masing-masing perusahaan memiliki fokus kebutuhan berbeda. Setiap sistem dalam machine learning dirancang khusus sesuai kebutuhan itu. Dengan kata lain, setiap perusahaan memiliki sistem khusus yang tidak bisa diterapkan lagi untuk perusahaan lainnya. Perlu waktu lama untuk memproses data besar Machine learning memang bisa memproses sejumlah data dengan waktu cepat. Namun, ketika volume data sangat besar, sistem memerlukan waktu lebih lama dan memungkinkan adanya error selama pemrosesan. Selain itu, semakin canggih sistem, proses pembuatan program bisa mencapai waktu bertahun-tahun. Hal ini dikarenakan sistem membutuhkan data lebih banyak dan kompleks untuk bisa menghasilkan fitur-fitur canggih.",
    cue_points="• data<br/>• learning<br/>• machine<br/>• algoritma<br/>• sistem<br/>• mesin<br/>• belajar<br/>• salah<br/>• manusia<br/>• kesalahan<br/>• pembelajaran<br/>• teknologi<br/>• memiliki<br/>• output<br/>• perusahaan<br/>• akurat<br/>• pola<br/>• canggih<br/>• anak<br/>• huruf<br/>• dipelajari<br/>• proses<br/>• pekerjaan<br/>• dikeluarkan<br/>• pembuatan<br/>• khusus<br/>• model<br/>• pengetahuan<br/>• fungsi<br/>• hasil",
    summary="Hal yang membedakan pembelajaran manusia dan mesin adalah manusia belajar dari pengalaman masa lalu, sementara machine learning belajar dari data. Kumpulan data ini melatih algoritma machine learning mengklasifikasikan data atau memprediksi hasil secara akurat. Machine learning adalah salah satu bagian dari artificial intelligence yang memungkinkan mesin belajar dari data atau pengalaman masa lalu (data historis) sehingga tidak perlu diprogram secara manual untuk melakukan seluruh pekerjaan. Unsupervised learning adalah jenis machine learning yang memberikan pembelajaran kepada kumpulan data tidak berlabel (unlabeled data). Itu sebabnya data menjadi objek penting dalam membuat machine learning. Machine learning memang bisa memproses sejumlah data dengan waktu cepat. Pembelajaran mesin bergantung besar pada data dan algoritma. Supervised learning adalah jenis pembelajaran di mana scientist memberikan sampel data berlabel (labeled data) kepada mesin. Pemberian sampel data bertujuan untuk melatih sistem dalam mempelajari kumpulan data dan berakhir dengan menguji model machine learning yang telah terbentuk. Kesalahan kecil dalam algoritma mengakibatkan output pembelajaran yang salah. Tanpa data, machine tidak mendapatkan pengetahuan apa pun yang bisa dipelajari. Dalam konteks yang lebih sederhana, metode machine learning mirip dengan cara belajar manusia. Teknik machine learning memiliki jangkauan sangat luas. Teknologi machine learning hadir untuk melakukan fungsi tersebut. Teknologi machine learning memungkinkan kualitas pekerjaan meningkat. Hasil pengelompokan data tersebut melatih mesin untuk belajar secara mandiri dari data-data yang ada, termasuk pola tersembunyi dalam data, sehingga campur tangan menusia menjadi sangat minimal. Setiap sistem dalam machine learning dirancang khusus sesuai kebutuhan itu. Setiap ada ketidakcocokan dalam data apa pun, seluruh sistem menjadi tidak akurat.",
    filename="contoh_laporan.pdf"
)