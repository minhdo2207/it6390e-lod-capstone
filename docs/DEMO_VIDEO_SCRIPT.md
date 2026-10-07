# Kịch bản video demo (≈ 4 phút 40) — vừa nói vừa thao tác

Người quay: Chiến. Quay màn hình + thu tiếng (QuickTime: File > New Screen Recording). Lời thoại tiếng Việt; thuật ngữ giữ tiếng Anh.
Mỗi cảnh có: **màn hình/thao tác** (làm gì, gõ gì) và **lời thoại** (đọc to). Đọc chậm hơn bình thường một chút, mỗi cảnh làm thao tác trước 1-2 giây rồi mới nói.

---

## Chuẩn bị trước khi quay (làm 1 lần, ~10 phút)

```bash
git clone https://github.com/minhdo2207/it6390e-lod-capstone
cd it6390e-lod-capstone
pip install -r requirements.txt owlready2     # owlready2 + Java chỉ cần cho cảnh 3
```

Tạo 2 file cho Protégé (để Desktop, **không commit**): một file đủ ontology + dữ liệu, một file thêm phim "lỗi" để demo mâu thuẫn.

```bash
python - <<'EOF'
from rdflib import Graph
import os
out = os.path.expanduser("~/Desktop/")
g = Graph()
for f in ["ontology/movies.ttl", "data/processed/movies_linked.ttl", "data/processed/awards.ttl"]:
    g.parse(f)
g.serialize(out + "demo_all.ttl", format="turtle")
g.parse("ontology/demo_inconsistency.ttl")
g.serialize(out + "demo_all_bad.ttl", format="turtle")
EOF
```

Kiểm tra trước, mỗi lệnh phải chạy ra kết quả (nếu không thì xem mục "Nếu lỗi" cuối file):
- `python scripts/sparql_cli.py -n 3` → bảng 5 đạo diễn (Spielberg 8, Tarantino 7, Nolan 7...)
- `python scripts/sparql_cli.py -n 6` → ngày sinh Nolan **1970-07-30** (cần internet)
- `python scripts/check_reasoning.py` → `ActionMovie: 29 / ComedyMovie: 16 / AwardWinningDirector: 32 / ActorDirector: 5`
- Mở Protégé, File > Open `demo_all.ttl`, bấm **Reasoner > Start reasoner (HermiT)** thử một lần cho chắc chạy được.

Mẹo quay: tăng cỡ chữ terminal (Cmd + `+`), đóng thông báo/tab thừa, tắt chế độ làm phiền, quay 1080p. Quay từng cảnh riêng rồi ghép sẽ dễ sửa hơn quay một mạch.

---

## Cảnh 1 — Giới thiệu (0:00 – 0:25)

**Màn hình:** trang GitHub repo `it6390e-lod-capstone`, cuộn qua README (mục Goal và Pipeline).

**Lời thoại:**
> "Xin chào, đây là demo project capstone của nhóm 2, môn Knowledge Graphs. Nhóm xây một knowledge graph về 250 bộ phim từ dữ liệu TMDB, đi đủ năm bước của đề bài: ontology, thu thập dữ liệu, chuyển sang RDF bốn sao, liên kết sang Wikidata và DBpedia để lên năm sao, và truy vấn bằng SPARQL. Trong video này mình demo ba phần: ontology cùng reasoner, dữ liệu liên kết, và truy vấn."

---

## Cảnh 2 — Ontology trong Protégé (0:25 – 1:05)

**Màn hình:** Protégé với `demo_all.ttl`. Tab **Entities > Classes**: mở rộng `Movie`, `Person` (thấy `Director`, `Actor`), rồi bấm vào `ActionMovie`; panel **Equivalent To** hiện `hasGenre value genre_action`. Cuối cảnh bấm tab **Object properties**, chỉ `dbo:director`, `dbo:starring`, `hasCastRole`.

**Lời thoại:**
> "Đây là ontology trong Protégé. Nhóm dùng lại từ vựng có sẵn: Movie của schema.org, Person của FOAF, director và starring của DBpedia, chỉ tự định nghĩa thêm những thứ chưa có như hasGenre hay CastRole. Chú ý lớp ActionMovie: nó được định nghĩa bằng equivalentClass, nghĩa là *phim nào có genre là Action thì thuộc ActionMovie*. Vì là equivalentClass, điều kiện này vừa cần vừa đủ, nên máy có thể tự phân loại. Mình sẽ cho reasoner chạy ngay đây."

---

## Cảnh 3 — Reasoner phân loại tự động (1:05 – 2:00)

**Màn hình:**
1. Menu **Reasoner > Start reasoner** (HermiT), chờ vài giây tới khi hiện trạng thái xong.
2. Mở **Window > Tabs > DL Query**. Gõ `ActionMovie`, tick **Instances**, bấm **Execute**. Cuộn danh sách.
3. Chuyển sang terminal, chạy: `python scripts/check_reasoning.py` và chỉ vào 4 dòng kết quả.

**Lời thoại:**
> "Mình bấm Start reasoner, dùng HermiT. Giờ hỏi trong DL Query: những cá thể nào thuộc ActionMovie. Máy trả về danh sách phim hành động, trong khi không có phim nào được gắn nhãn ActionMovie bằng tay, tất cả được suy ra từ genre. *[nếu danh sách dài gấp ba lần 29: "Danh sách dài hơn vì mỗi phim còn có URI Wikidata và DBpedia được nối bằng sameAs, máy coi chúng là cùng một thực thể; tính riêng phim của nhóm thì đúng 29."]*
> Cùng cách đó, nhóm có ComedyMovie 16 phim, AwardWinningDirector 32 đạo diễn thắng giải Oscar, lấy từ Wikidata. Còn ActorDirector, tức người vừa đạo diễn vừa đóng chính trong cùng một phim, có 5 người: Clint Eastwood, Mel Gibson, Kevin Costner, Woody Allen, Terry Gilliam. Lớp này không viết được bằng restriction của OWL mà phải dùng một SWRL rule. Đây là bốn con số mình chạy lại bằng script để đối chiếu."

---

## Cảnh 4 — Dữ liệu và liên kết 5 sao (2:00 – 2:30)

**Màn hình:** terminal, chạy:
```bash
grep -n -A16 "resource/movie/1124> a" data/processed/movies_linked.ttl
```
Chỉ chuột vào hai dòng cuối `owl:sameAs` (DBpedia và Wikidata).

**Lời thoại:**
> "Đây là bộ phim The Prestige trong dữ liệu RDF: có đạo diễn, ba diễn viên, genre, hãng phim và năm phát hành. Hai dòng cuối là điểm quan trọng: owl:sameAs nối phim này với trang DBpedia và với mục Q46551 trên Wikidata. Đó là ngôi sao thứ năm. Nhóm có 920 liên kết Wikidata và 912 liên kết DBpedia. Nhóm khớp bằng TMDB id mà Wikidata lưu sẵn, không khớp theo tên phim, vì thử khớp theo tên và năm thì không ra kết quả nào. Nhóm cũng tự kiểm tra 30 liên kết: Wikidata đúng cả 30, DBpedia đúng 29."

---

## Cảnh 5 — Truy vấn SPARQL local (2:30 – 3:10)

**Màn hình:** terminal, chạy lần lượt:
```bash
python scripts/sparql_cli.py -n 3
python scripts/sparql_cli.py -n 16
```
(Bảng 1: Spielberg 8 phim. Bảng 2: The Dark Knight, cast gồm Christian Bale / Bruce Wayne, Heath Ledger / Joker, Aaron Eckhart / Harvey Dent.)

**Lời thoại:**
> "Giao diện truy vấn của nhóm là terminal cộng với tab SPARQL của Protégé. Query số 3 trả lời câu hỏi đạo diễn nào có nhiều phim nhất trong dữ liệu: Spielberg với 8 phim. Query số 16 dùng CastRole, mô hình quan hệ n-ary: mỗi lần một diễn viên xuất hiện trong phim là một nút riêng, nên ghi được cả nhân vật và thứ tự đứng tên. Ví dụ The Dark Knight: Christian Bale đóng Bruce Wayne, Heath Ledger đóng Joker. Quan hệ starring thông thường chỉ nối phim với diễn viên, không chứa được thông tin này."

---

## Cảnh 6 — Truy vấn liên kết (federated) (3:10 – 3:50)

**Màn hình:** terminal, chạy `python scripts/sparql_cli.py -n 6` (cần internet; đợi vài giây). Kết quả: Christopher Nolan, 1970-07-30, London, kèm 7 phim.

**Lời thoại:**
> "Phần hay nhất là query liên kết. Dữ liệu nhóm không có ngày sinh của đạo diễn. Query này lấy đường link sameAs của Christopher Nolan, dùng lệnh SERVICE để hỏi thẳng Wikidata, rồi ghép câu trả lời với các phim của ông trong dữ liệu của nhóm. Kết quả: Nolan sinh ngày 30 tháng 7 năm 1970 tại London, kèm bảy phim từ Memento đến Interstellar. Nhờ liên kết năm sao mà dữ liệu của nhóm được bổ sung từ nguồn bên ngoài chỉ trong một câu truy vấn."

---

## Cảnh 7 — Reasoner bắt mâu thuẫn (3:50 – 4:25)

**Màn hình:** Protégé: **File > Open** `demo_all_bad.ttl` (nếu hỏi, chọn mở trong cửa sổ mới) → **Reasoner > Start reasoner**. Hiện hộp thoại ontology inconsistent → bấm **Explain** và để lên màn hình danh sách giải thích khoảng 3 giây.

**Lời thoại:**
> "Cuối cùng, reasoner cũng bắt được lỗi. Mình nạp thêm một bộ phim cố ý sai: nó được gán vừa genre Action vừa genre Comedy, trong khi hai lớp ActionMovie và ComedyMovie được khai báo disjoint, nghĩa là không thể cùng lúc. Bấm Start reasoner, HermiT báo ontology bị inconsistent, và nút Explain chỉ ra đúng nguyên nhân. Đây cùng kiểu với ví dụ nghịch lý Russell trong bài giảng, và là lý do cần khai báo disjoint tường minh, vì mặc định Semantic Web theo Open World Assumption sẽ không tự coi đó là mâu thuẫn."

---

## Cảnh 8 — Kết (4:25 – 4:45)

**Màn hình:** quay lại trang GitHub, hoặc slide cuối.

**Lời thoại:**
> "Tóm lại, nhóm đã đi đủ năm bước: ontology, dữ liệu, RDF, liên kết, và SPARQL, thêm reasoning và truy vấn liên kết. Hạn chế hiện tại là URI còn dùng example.org nên chưa truy cập được qua web, và mỗi phim mới giữ một genre. Toàn bộ mã nguồn có trên GitHub của nhóm. Cảm ơn đã xem."

---

## Nếu lỗi khi quay (phương án dự phòng)

| Sự cố | Cách xử lý |
|---|---|
| `-n 6` báo lỗi hoặc rỗng (Wikidata chậm / giới hạn tốc độ) | Chờ 30 giây chạy lại. Vẫn lỗi thì thêm `-v`, hoặc chạy query khác `-n 11` (DBpedia) và nói vẫn theo ý đó; hoặc dùng ảnh chụp kết quả đã chụp từ trước. |
| Protégé không chạy HermiT / báo thiếu bộ nhớ | Reasoner > Configure, hoặc mở lại Protégé; nếu vẫn lỗi, quay phần terminal `python scripts/check_reasoning.py --demo` (in ra đủ 29/16/32/5 và dòng `ontology is INCONSISTENT`), thay cho cảnh 3 và 7. |
| DL Query không hiện lệnh | Window > Tabs > chọn DL Query; phải **Start reasoner** trước. |
| Danh sách DL Query dài gấp ~3 lần 29 | Bình thường (cá thể sameAs); nói câu trong ngoặc ở cảnh 3. |
| Hộp thoại Open hỏi merge hay cửa sổ mới | Chọn mở cửa sổ mới (không merge). |
| Protégé không đọc được `.ttl` | Dùng File > Open và chọn "All files"; Protégé 5.6 đọc được Turtle. |

**Những chỗ chưa được thử trên Protégé thật** (nhóm chưa mở GUI để chạy, hãy thử một lần trước khi quay và sửa lời thoại cho khớp): hình dạng danh sách trong DL Query (có thể dài hơn 29 dòng), hộp thoại Open khi mở file thứ hai, và nút Explain.
