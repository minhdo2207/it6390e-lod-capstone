# Report Content — Movies Linked Open Data Knowledge Graph
### IT6390E Knowledge Graphs — Group 2

*Dùng nội dung dưới đây để soạn Report (≤15 trang, Word/Google Docs). Mỗi mục lớn tương ứng 1 phần đề bài. Chỗ nào ghi "[Chèn ảnh]"/"[Chèn bảng kết quả]" là chỗ cần chèn screenshot Protégé thật khi đã làm xong.*

---

## 1. Giới thiệu (Introduction) — ~1 trang

- Bối cảnh: Linked Open Data (LOD) và 5-star deployment scheme (Tim Berners-Lee, 2010).
- Mục tiêu project: xây dựng knowledge graph cho domain **Phim ảnh (Movies)**, đạt chuẩn 5-star, có khả năng truy vấn qua SPARQL.
- Lý do chọn domain: dữ liệu mở phong phú (TMDB/Kaggle), có sẵn liên kết dày đặc tới DBpedia/Wikidata → khả thi trong thời gian ngắn, đồng thời minh hoạ tốt các khái niệm đã học (RDF, RDFS, OWL, LOD).
- Công cụ sử dụng: **Protégé** (soạn ontology, reasoning, demo), **Python + RDFLib** (pipeline CSV→RDF, linking), **HermiT reasoner**, **SPARQL Query tab** (Protégé).

## 2. Bước 1 — Định nghĩa Ontology — ~4 trang

### 2.1 Competency Questions
Liệt kê (xem `docs/PROJECT_PLAN.md`):
- Phim X được đạo diễn bởi ai?
- Những phim nào có diễn viên Y?
- Phim thể loại G phát hành sau năm Y?
- Đạo diễn nào có nhiều phim nhất?

### 2.2 Lớp (Classes) và thuộc tính (Properties)
Chèn bảng class/property đã có trong `ontology/movies.ttl` (Movie, Person, Director, Actor, Genre, Studio, Country + các property, ghi rõ property nào **reuse** từ vocabulary có sẵn: `foaf:Person`, `schema:Movie`, `dbo:director`, `dbo:starring`, `dc:title`).

**Giải thích lựa chọn thiết kế (quan trọng — thể hiện áp dụng kiến thức Knowledge Modeling lecture):**
- Ưu tiên tái sử dụng vocabulary có sẵn (FOAF, Dublin Core, schema.org, DBpedia Ontology) trước khi tự định nghĩa mới → đúng Best Practice #3-#5 của LOD.
- Thảo luận ngắn về **OntoClean**: `Director`/`Actor` về bản chất là *role* (vai trò tạm thời) chứ không phải *rigid type* — nếu soi theo test Rigidity thì đúng ra nên model bằng property (`hasRole`) thay vì subclass cố định của `Person`. Nhóm chọn giữ dạng subclass vì đơn giản hoá phạm vi capstone, nhưng ghi nhận đây là trade-off có ý thức (không phải thiếu hiểu biết).

### 2.3 Defined classes bằng Restriction (giống pattern pizza.owl — điểm nhấn demo)
Đây là phần giúp reasoner "tự làm việc" trực tiếp trong Protégé, giống cách `pizza.owl` định nghĩa `VegetarianPizza`:

```turtle
:ActionMovie owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty :hasGenre ;
    owl:hasValue :genre/action
] .

:AwardWinningDirector owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty :directed ;
    owl:someValuesFrom [
        a owl:Restriction ;
        owl:onProperty :hasAward ;
        owl:someValuesFrom owl:Thing
    ]
] .
```
→ Khi chạy reasoner (HermiT) trong Protégé, các phim thuộc genre "Action" sẽ **tự động được phân loại** vào `ActionMovie` mà không cần gán thủ công — đây chính là phần demo trực quan nhất, tương tự bài Sudoku/pizza.owl đã học.

**[Chèn ảnh]** Screenshot Protégé — Class hierarchy trước và sau khi chạy reasoner (before/after inferred classes).

## 3. Bước 2 — Thu thập dữ liệu — ~1.5 trang

- Nguồn: TMDB/Kaggle (ghi rõ tên dataset + link + license).
- Phạm vi: số lượng phim thực tế đã lấy (250 phim, 1939–2016), tiêu chí lọc (ít nhất 1000 votes, top 250 theo rating).
- Các trường dữ liệu: title, year, director, cast, genre, studio, country.
- Vấn đề làm sạch dữ liệu gặp phải (nếu có): tên trùng, thiếu dữ liệu đạo diễn, encoding...

**[Chèn bảng]** Ví dụ 5-10 dòng dữ liệu thô (CSV) trước khi convert.

## 4. Bước 3 — Chuyển sang 4-star — ~2 trang

- Công cụ: script `scripts/csv_to_rdf.py` (RDFLib) — mô tả ngắn cách hoạt động (đọc CSV → sinh URI → gán class/property → serialize Turtle).
- Giải thích vì sao đạt 4-star: dữ liệu ở **RDF** (chuẩn W3C), dùng **URI** để định danh (không phải string tự do), format **non-proprietary** (Turtle).
- Số liệu: tổng số triple sinh ra, số class/instance.

**[Chèn ảnh]** Screenshot 1 đoạn file `.ttl` sau khi convert + screenshot import vào Protégé thành công (Individuals tab).

## 5. Bước 4 — Liên kết đạt 5-star — ~2 trang

- Công cụ: script `scripts/link_wikidata_dbpedia.py` — match theo **TMDB id** lưu trong Wikidata (P4947 phim, P4985 người), rồi lấy URI DBpedia từ `owl:sameAs` của DBpedia. Cách match theo title + year không dùng được vì resource phim trên DBpedia không có `dbo:releaseDate`.
- Nguyên tắc dùng `owl:sameAs` đúng cách (dẫn lại từ LOD lecture): chỉ link khi chắc chắn cùng 1 thực thể; trường hợp không chắc → bỏ qua thay vì đoán (khác với các lỗi lạm dụng `owl:sameAs` đã học — VD nhầm state với city, nhầm instance với organization).
- Kết quả: phim 249/250 link Wikidata và DBpedia; người 671/672 Wikidata, 667/672 DBpedia (xem `data/processed/link_report.csv`). 2 resource bỏ qua vì mơ hồ: Apocalypse Now, J.K. Simmons.
- (Tuỳ chọn nếu có thời gian) Link thêm Wikidata.
- Kiểm tra thủ công: mẫu ngẫu nhiên 30 resource (15 phim, 15 người, `random.seed(42)`, script `scripts/sample_link_check.py`), mở từng trang Wikidata và DBpedia để đối chiếu năm + đạo diễn (phim) hoặc mô tả nghề nghiệp + ngày sinh (người). Kết quả trong `docs/link_check.csv`: **precision Wikidata 30/30 = 100%**, **precision DBpedia 29/30 = 96,7%**.
- Link sai duy nhất trong mẫu: `dbr:Alakina_Mann` trên DBpedia là resource redirect sang phim `dbr:The_Others_(2001_film)` (bài Wikipedia về diễn viên đã bị gộp vào bài về phim), nên không còn mô tả đúng người này. Kiểm tra toàn bộ 916 link DBpedia thì có 7 resource là redirect: 3 chỉ do đổi tên bài (cùng thực thể), 4 trỏ sang thực thể khác (Alakina Mann → phim; Joel Coen → Coen brothers; Anthony Russo → Russo brothers; Lilly Wachowski → The Wachowskis).

**[Chèn ảnh]** Screenshot Protégé — 1 individual Movie có property `owl:sameAs` trỏ tới DBpedia resource (Object property assertions panel).

## 6. Bước 5 — SPARQL Query Interface — ~2 trang

- Công cụ: **terminal** `python scripts/sparql_cli.py` (prompt tương tác hoặc `-n <số>`), và **Protégé SPARQL Query tab** (Window → Tabs → SPARQL Query).
- Liệt kê 3-4 câu SPARQL demo (từ `sparql/sample_queries.rq`), giải thích từng câu trả lời competency question nào ở mục 2.1.

**[Chèn ảnh]** Screenshot chạy từng câu SPARQL trong Protégé + kết quả trả về.

(Nếu nhóm có thời gian dựng thêm Apache Jena Fuseki làm SPARQL HTTP endpoint thật sự, ghi thêm phần này — không bắt buộc vì đề bài chấp nhận "SPARQL endpoint/**terminal**".)

## 7. Kết luận — ~0.5 trang

- Tóm tắt: đã đạt 5-star hay chưa, những gì làm được/chưa làm được.
- Hạn chế cần nêu thẳng: URI của nhóm dùng `example.org` nên **chưa dereferenceable** (chưa đạt trọn nguyên lý Linked Data số 2); mỗi phim chỉ giữ 1 genre chính; dataset không có dữ liệu giải thưởng nên phải bổ sung Oscar Best Director từ Wikidata; ghi nguồn TMDb.
- Bài học rút ra khi áp dụng RDF/RDFS/OWL/LOD vào 1 bài toán thực tế.
- Hướng phát triển tiếp (nếu có thêm thời gian): mở rộng dataset, dùng Silk Framework để tự động hoá linking, dựng SPARQL endpoint HTTP thật.

## 8. Phân công (Role Division) — ~0.5 trang
Chèn bảng từ `docs/ROLES.md`.

## 9. Tài liệu tham khảo (References)
- https://5stardata.info/en/
- https://lod-cloud.net/
- https://www.dbpedia.org/resources/sparql/
- https://protege.stanford.edu/
- Slide bài giảng IE650/IT6390E: Introduction, RDF, RDFS, LOD, OWL, OWL2, Knowledge Modeling
- Nguồn dataset phim đã dùng (ghi rõ tên + link)
