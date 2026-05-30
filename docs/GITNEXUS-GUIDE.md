# Hướng dẫn Sử dụng GitNexus trong Windsurf

> **Mục tiêu:** Giúp bạn dùng GitNexus hiệu quả nhất — hiểu rõ khi nào dùng tool nào, tránh sai lầm phổ biến, và tiết kiệm thời gian.

---

## GitNexus là gì?

GitNexus là một **"bản đồ thông minh"** cho code của bạn. Thay vì phải tự đọc hàng trăm file để hiểu code hoạt động ra sao, GitNexus đã phân tích sẵn và trả lời bạn ngay lập tức.

**Hình dung đơn giản:**
- Codebase của bạn = một thành phố lớn
- GitNexus = bản đồ GPS đã đánh dấu mọi con đường, tòa nhà, và mối liên kết
- Bạn chỉ cần **hỏi** — không cần tự đi tìm

---

## 7 Tools — Khi nào dùng cái nào?

GitNexus cung cấp 7 tools. Dưới đây là cách chọn đúng tool cho đúng tình huống:

### 🔍 `query` — "Tìm cho tôi cách X hoạt động"

**Khi nào dùng:** Khi bạn muốn hiểu **luồng hoạt động** của một tính năng/chức năng.

| Tình huống ví dụ | Câu hỏi |
|---|---|
| "Xử lý ảnh đầu vào chạy qua những bước nào?" | `query: "image processing pipeline"` |
| "PCI được tính như thế nào?" | `query: "PCI calculation flow"` |
| "Phát hiện hư hỏng hoạt động ra sao?" | `query: "damage detection"` |

**Kết quả:** Trả về các **luồng thực thi** (processes) — chuỗi các hàm được gọi theo thứ tự, kèm vị trí file. Giống như xem bản đồ đường đi từ A đến Z.

**💡 Mẹo:** Dùng `query` **trước** khi đọc code. Nó cho bạn bức tranh toàn cảnh, giúp bạn đọc code có chủ đích hơn.

---

### 🎯 `context` — "Cho tôi mọi thông tin về hàm/class X"

**Khi nào dùng:** Khi bạn cần **hiểu sâu** về một symbol cụ thể (hàm, class, method).

| Tình huống ví dụ | Cách gọi |
|---|---|
| "Ai gọi hàm `calculate_pci`?" | `context: name="calculate_pci"` |
| "Class `PCIEngine` có những method gì?" | `context: name="PCIEngine"` |
| "Hàm `segment_image` phụ thuộc vào ai?" | `context: name="segment_image"` |

**Kết quả:** 360° view — tất cả mối quan hệ:
- **Ai gọi nó** (incoming calls)
- **Nó gọi ai** (outgoing calls)
- **Nó tham gia luồng nào** (process participation)
- **Nó nằm ở module nào** (community)

**💡 Mẹo:** Dùng `context` **sau** `query` — khi bạn đã tìm được symbol quan trọng và muốn đào sâu.

---

### 💥 `impact` — "Nếu tôi sửa X, cái gì sẽ hỏng?"

**Khi nào dùng:** **TRƯỚC KHI SỬA CODE** — bắt buộc theo quy tắc AGENTS.md.

| Tình huống ví dụ | Cách gọi |
|---|---|
| "Sửa hàm `calculate_pci` ảnh hưởng gì?" | `impact: target="calculate_pci", direction="upstream"` |
| "Class `RoadDamageDetector` phụ thuộc vào ai?" | `impact: target="RoadDamageDetector", direction="downstream"` |

**Kết quả:** Báo cáo "bán kính ảnh hưởng":
- **d=1 (WILL BREAK):** Những hàm gọi trực tiếp → **chắc chắn bị ảnh hưởng**
- **d=2 (LIKELY AFFECTED):** Ảnh hưởng gián tiếp
- **d=3 (MAY NEED TESTING):** Nên test lại
- **Mức độ rủi ro:** LOW / MEDIUM / HIGH / CRITICAL

**⚠️ QUAN TRỌNG:** Nếu `impact` trả về **HIGH** hoặc **CRITICAL** → phải cảnh báo cho bạn trước khi sửa.

**💡 Mẹo:** `direction="upstream"` = "ai phụ thuộc vào tôi?" (dùng trước khi sửa). `direction="downstream"` = "tôi phụ thuộc vào ai?" (dùng khi debug).

---

### 🔬 `detect_changes` — "Thay đổi của tôi ảnh hưởng gì?"

**Khi nào dùng:** **TRƯỚC KHI COMMIT** — kiểm tra xem những thay đổi chưa commit có ảnh hưởng ngoài ý muốn không.

| Tình huống | Cách gọi |
|---|---|
| Kiểm tra unstaged changes | `detect_changes: scope="unstaged"` |
| Kiểm tra staged changes | `detect_changes: scope="staged"` |
| Kiểm tra tất cả | `detect_changes: scope="all"` |
| So sánh với branch main | `detect_changes: scope="compare", base_ref="main"` |

**Kết quả:** Liệt kê symbols bị thay đổi + processes bị ảnh hưởng + tóm tắt rủi ro.

---

### ✏️ `rename` — "Đổi tên symbol an toàn trên toàn bộ codebase"

**Khi nào dùng:** Khi cần đổi tên hàm, class, method, biến — **không dùng find-and-replace thủ công**.

| Tình huống | Cách gọi |
|---|---|
| Đổi tên `calculate_pci` thành `compute_pci` | `rename: symbol_name="calculate_pci", new_name="compute_pci"` |
| Xem trước (không sửa file) | `rename: dry_run=true` (mặc định) |

**Kết quả:** Danh sách tất cả vị trí cần đổi, kèm **độ tin cậy**:
- `graph` = tìm qua knowledge graph → **tin cậy cao, an toàn**
- `text_search` = tìm qua regex → **cần xem xét kỹ trước khi chấp nhận**

**💡 Mẹo:** Luôn chạy `dry_run=true` trước. Xem kết quả, xác nhận đúng rồi mới chạy `dry_run=false`.

---

### 🗺️ `route_map` — "API endpoints kết nối với ai?"

**Khi nào dùng:** Khi cần hiểu API routes — handler nào phục vụ route nào, component nào gọi route nào.

| Tình huống | Cách gọi |
|---|---|
| Xem tất cả routes | `route_map:` (không tham số) |
| Xem route cụ thể | `route_map: route="/api/grants"` |

---

### 🧮 `cypher` — "Truy vấn nâng cao"

**Khi nào dùng:** Khi các tool trên không đủ — cần truy vấn phức tạp vào knowledge graph.

**Yêu cầu:** Biết cú pháp Cypher (giống Neo4j). Chỉ dùng khi bạn đã quen với các tool cơ bản.

---

## Quy trình Làm việc Tối ưu

### Khi BẮT ĐẦU làm việc với code chưa quen:

```
1. query  → Hiểu luồng hoạt động tổng thể
2. context → Đào sâu vào symbol quan trọng
3. Sửa code (có impact check trước)
```

### Khi SỬA CODE:

```
1. impact  → Kiểm tra bán kính ảnh hưởng (BẮT BUỘC)
2. Sửa code
3. detect_changes → Kiểm tra trước khi commit (BẮT BUỘC)
```

### Khi DEBUG:

```
1. query   → Tìm luồng thực thi liên quan đến bug
2. context → Xem chi tiết symbol bị nghi ngờ
3. impact  → Kiểm tra trước khi áp dụng fix
```

### Khi REFACTOR/RENAME:

```
1. impact  → Kiểm tra rủi ro
2. rename (dry_run=true) → Xem trước
3. rename (dry_run=false) → Thực hiện
4. detect_changes → Xác nhận
```

---

## Resources — Xem thông tin tổng quan

Ngoài tools, GitNexus cung cấp **resources** (dữ liệu tĩnh, xem trực tiếp):

| Resource | Nội dung | Khi nào xem |
|----------|----------|-------------|
| `gitnexus://repo/dumps/context` | Tổng quan project + danh sách tools | Kiểm tra index còn mới không |
| `gitnexus://repo/dumps/clusters` | Các module/khu vực chức năng | Hiểu cấu trúc tổng thể |
| `gitnexus://repo/dumps/processes` | Tất cả luồng thực thi | Tìm luồng liên quan |
| `gitnexus://repo/dumps/process/{name}` | Chi tiết từng luồng (từng bước) | Đào sâu vào 1 luồng |

---

## Lỗi Phổ biến & Cách Tránh

| ❌ Sai | ✅ Đúng |
|--------|---------|
| Dùng `grep`/`find` để tìm hàm | Dùng `query` hoặc `context` — nhanh hơn và hiểu mối quan hệ |
| Sửa code không kiểm tra impact | Luôn chạy `impact` trước khi sửa |
| Dùng find-and-replace để đổi tên | Dùng `rename` — hiểu call graph, an toàn hơn |
| Commit không kiểm tra | Chạy `detect_changes` trước khi commit |
| Bỏ qua cảnh báo HIGH/CRITICAL | **Phải cảnh báo** cho người dùng trước khi tiếp tục |

---

## Bảo trì Index

GitNexus phân tích code tại một thời điểm. Khi code thay đổi, index có thể **lạc hậu** (stale).

**Cách kiểm tra:**
- Mỗi khi gọi tool, nếu GitNexus cảnh báo "index is stale" → cần cập nhật

**Cách cập nhật:**
```bash
npx gitnexus analyze
# hoặc (nếu cài global):
gitnexus analyze
```

**Khi nào cần cập nhật:**
- Sau khi thêm/xóa/sửa file quan trọng
- Sau khi merge branch lớn
- Khi tool trả về kết quả không còn chính xác

---

## Thông tin Kỹ thuật (tham khảo)

| Mục | Giá trị |
|-----|---------|
| Project | `dumps` |
| Symbols đã index | 1,864 |
| Mối quan hệ | 2,483 |
| Luồng thực thi | 40 |
| Modules | Tests (53), Ui (48), Engine (16), Scripts (6), Widgets (5) |
| Phiên bản GitNexus | 1.6.5 |
| MCP Config | `~/.codeium/windsurf/mcp_config.json` |
| Node path (Windsurf) | `C:/Users/Frank/AppData/Roaming/fnm/node-versions/v26.1.0/installation/node.exe` |

---

## Tóm tắt Nhanh

| Bạn muốn... | Dùng tool |
|-------------|-----------|
| Hiểu cách code hoạt động | `query` |
| Hiểu sâu 1 hàm/class | `context` |
| Biết sửa X sẽ hỏng gì | `impact` |
| Kiểm tra trước khi commit | `detect_changes` |
| Đổi tên an toàn | `rename` |
| Xem API routes | `route_map` |
| Truy vấn nâng cao | `cypher` |
