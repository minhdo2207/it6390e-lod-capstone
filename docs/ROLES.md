# Role Division — Group 2 (3 members)

| Member | Role | Việc cụ thể | Thuyết trình? |
|---|---|---|---|
| **Minh (trưởng nhóm)** | Ontology + Reasoning + Demo lead | - Thiết kế ontology trong Protégé (classes, properties, restrictions kiểu pizza.owl để reasoner tự phân loại được)<br>- Chạy reasoner (HermiT), xử lý lỗi/inconsistency nếu có<br>- Chuẩn bị + chạy demo trực tiếp (Protégé + SPARQL Query tab)<br>- Tổng hợp kỹ thuật, review toàn bộ trước khi nộp | ✅ Có (phần demo kỹ thuật) |
| **Đức** | Data + Linking | - Thu thập & làm sạch data phim (CSV, ~150-300 phim)<br>- Chạy `csv_to_rdf.py` để ra file .ttl (4-star)<br>- Chạy `link_dbpedia.py` để link DBpedia/Wikidata (5-star), review thủ công các match<br>- Hỗ trợ chuẩn bị slide phần data/pipeline | ✅ Có (phần data/pipeline) |
| **Chiến** | Report + Slide + Video | - Viết Report (≤15 trang) dựa trên nội dung Minh/Đức cung cấp<br>- Format slide (nội dung do Minh/Đức đưa, Chiến trình bày đẹp)<br>- Quay & dựng video demo (3-5 phút)<br>- Không thuyết trình trực tiếp | ❌ Không |

**Lưu ý phân bổ khối lượng:** Minh và Đức đảm nhiệm phần kỹ thuật (nặng hơn, cần thuyết trình), Chiến đảm nhiệm phần tổng hợp/trình bày tài liệu (nhẹ hơn, không cần đứng thuyết trình) — đúng như thống nhất của nhóm.

**Timeline bám theo phân công** (xem thêm `docs/PROJECT_PLAN.md`):
- Ngày 1-2: Minh chốt ontology sketch, Đức bắt đầu tìm nguồn data
- Ngày 3-6: Đức chạy pipeline 4-star/5-star song song Minh hoàn thiện ontology + restrictions trong Protégé
- Ngày 7: Minh tích hợp data đã link vào Protégé, test reasoner + SPARQL tab
- Ngày 8-9: Chiến viết report + làm slide + quay video (dựa trên kết quả 2 bạn kia)
- Ngày 10: Minh (+ Đức) trình bày
