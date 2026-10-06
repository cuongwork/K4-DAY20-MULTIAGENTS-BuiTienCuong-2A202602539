# Báo cáo Lab: Self evolving Agentic

Báo cáo trình bày kết quả thực hiện theo trình tự trong `GUIDE.md`. Tại thời điểm cập nhật ngày 06/10/2026, Phần 0–3 đã hoàn thành. Có chín lần chạy trên tập học thuộc ba điều kiện; Phần 4, giả thuyết và đóng băng skill chưa thực hiện.

## 1. Thông tin nhóm và cấu hình

Thực hiện cá nhân.

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Bùi Tiến Cường | 2A202602539 | Toàn bộ các phần triển khai, thí nghiệm, phân tích và báo cáo trong phạm vi bài thực hành. |

| Thành phần | Cấu hình |
|---|---|
| Mô hình | `gpt-4.1-mini` |
| Endpoint | `https://api.openai.com/v1` |
| Nhiệt độ | `LAB_TEMPERATURE=0` |
| Deep Agents | `0.7.21` |
| Môi trường kiểm tra trên Windows | Python `3.11.9`, môi trường ảo `.venv` |
| Môi trường thực thi Linux | Docker, image `lab-deepagents:latest`, Python `3.12.15` |
| Giới hạn đệ quy | 60 |
| Số lần chạy tác vụ | 9 lần trên tập học; tổng 507.984 token của runner; curator gọi một lần, token chưa được đo; ngân sách tổng chưa xác định |
| Tag `freeze` | Chưa tạo |

Image thực thi tác tử được dựng từ `Dockerfile` của kho mã nguồn. Kiểm tra Git/đóng băng sử dụng image dẫn xuất `lab-deepagents-verify` từ `report/Dockerfile.verify`; chỉ bổ sung Git, không thay đổi môi trường thực thi các lần chạy tác tử. Khóa API được lưu trong `.env`, thuộc danh sách loại trừ của Git.

## 2. Giả thuyết (Phần 4.0)

Các giả thuyết dưới đây được lập sau Phần 3, trước khi chạy hoặc xem điểm tác vụ đánh giá. Căn cứ gồm số liệu tập học, vết thực thi và lưu ý khoa học trong `guides/pseudocode/04_curator.md` về việc lợi ích trên tập học có thể không chuyển sang tác vụ mới. Đây là dự đoán cần kiểm chứng, không phải kết luận về tập đánh giá.

- H1 (subagents so với baseline): Dự đoán baseline có điểm đánh giá trung bình cao hơn subagents và dùng ít token hơn. Trên tập học, baseline đạt 44,54% so với 33,33%, trong khi subagents tăng token 69,54%; vết cho thấy thiếu hoặc biến đổi đặc tả khi giao việc và thiếu kiểm chứng đầu ra. Việc thêm subagent chưa bảo đảm cải thiện chất lượng.
- H2 (skills-auto so với baseline): Dự đoán skills-auto không cải thiện điểm đánh giá trung bình so với baseline; baseline được dự đoán là điều kiện tốt nhất. Hai skill tập trung miền code, chưa bao phủ quy ước data/logs và không được đọc trong cả ba lần chạy học; điểm học skills-auto đạt 41,20%, thấp hơn baseline. Nếu skill được đọc ở tập đánh giá, lợi ích dự kiến tập trung ở quy ước type hint chứ không bao phủ mọi check mới.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình đánh giá của skills-auto thấp hơn điểm học sau đóng băng, và hiệu quả học không chuyển đầy đủ sang dữ liệu mới. GUIDE nêu tác vụ đánh giá thêm quy ước mới; skill hiện có phạm vi hẹp. Chênh lệch giữa lần học trước và sau đóng băng của cùng bộ skill sẽ được dùng làm dấu hiệu nhiễu, không diễn giải toàn bộ thành hiệu quả học.

## 3. Cài đặt và làm quen Deep Agents (Phần 0)

### 3.1. Cài đặt

Môi trường ảo và các thư viện đã được thiết lập. Cấu hình mô hình được khai báo theo Option 1 của `.env.example`. Tệp báo cáo được khởi tạo từ `REPORT_TEMPLATE.md`; môi trường Linux được chuẩn bị bằng Docker để đáp ứng yêu cầu shell `/bin/sh`.

### 3.2. Kiểm tra môi trường

| Kiểm tra | Kết quả |
|---|---|
| `tests/test_01_provided.py` trên Windows, sử dụng thư mục tạm riêng | 12 passed; 4,46 giây |
| Dựng image bằng `docker build -t lab-deepagents .` | Thành công, mã thoát 0 |
| `tests/test_01_provided.py` trong container Linux | 12 passed; 4,45 giây |
| Thực thi `/bin/sh` trong container | Trả về `SHELL_OK` |
| Kết nối OpenAI trên máy chủ | Trả về `OK` |
| Kết nối OpenAI trong container | Trả về `OK` |

Lần kiểm tra thủ công ban đầu trên Windows ghi nhận 9 test đạt và 3 lỗi thiết lập do không có quyền truy cập thư mục `pytest-of-Admin`. Việc chỉ định thư mục tạm riêng bằng `--basetemp` khắc phục lỗi này. Kiểm tra API trong sandbox gặp `WinError 10013`; kiểm tra ngoài sandbox thành công, cho thấy hạn chế truy cập mạng của phiên chạy là nguyên nhân trực tiếp.

Hai yêu cầu kiểm tra API thành công sử dụng cùng nội dung `Reply with OK`. Đây là kiểm tra kết nối, không được tính là lần chạy tác vụ thí nghiệm. Các kết quả trên xác nhận môi trường đáp ứng yêu cầu của Phần 0.

### 3.3. Quan sát tác tử mặc định

Chương trình `scripts/tour.py` sử dụng mô hình giả, chạy thành công và không tiêu thụ token API.

1. Tác tử có chín công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. Công cụ `execute` cho phép thực thi lệnh shell.
2. Công cụ `task` khởi tạo subagent tạm thời. Subagent `general-purpose` hỗ trợ nghiên cứu, tìm kiếm và xử lý tác vụ nhiều bước, với cùng tập công cụ của tác tử chính. Mỗi lần gọi mặc định không lưu trạng thái; subagent chỉ nhận prompt được giao. Vì vậy, lời giao việc cần chứa đầy đủ yêu cầu và ngữ cảnh cần thiết.
3. System prompt mặc định là chuỗi rỗng. Mô tả `task` quy định: “The agent's report is not shown to the user; relay a summary yourself.” Mô tả `execute` hướng dẫn: “Quote paths containing spaces (e.g. cd \"/path/with spaces\").” Các mô tả công cụ cung cấp hướng dẫn hành vi dù system prompt mặc định rỗng.

### 3.4. Xây dựng backend và tác tử (bước 1.2)

Hàm `make_backend` sử dụng `LocalShellBackend` với thư mục gốc là sandbox, đường dẫn ảo và thời gian chờ 120 giây. Shell không kế thừa môi trường tiến trình cha; chỉ nhận `PATH`, `HOME` và `PYTHONDONTWRITEBYTECODE`. `PATH` chứa thư mục Python đang chạy cùng các thư mục hệ thống Linux, giúp thực thi Python mà không truyền khóa API vào shell.

Hàm `build_agent` hỗ trợ hai chế độ `single` và `subagents`; chế độ không hợp lệ gây `ValueError`. Chế độ `subagents` bổ sung các vai trò đã định nghĩa, nối `PATHS_NOTE` vào prompt từng subagent và thêm `SUBAGENTS_NOTE` vào prompt chính. Khi `use_skills=True`, tác tử nhận đường dẫn `/skills/` và `SKILLS_NOTE`. Mô hình giả có thể được truyền trực tiếp để kiểm tra ngoại tuyến.

Trước triển khai, `test_02_agent.py` ghi nhận 8 test thất bại và 1 test đạt do các hàm TODO. Sau triển khai, toàn bộ 9 test đạt trong 2,30 giây trên container Linux, bao gồm kiểm tra bảo vệ khóa API, thống nhất đường dẫn, công cụ, chế độ, skill và prompt của subagent. Bốn hằng số prompt được đối chiếu với bản gốc bằng cấu trúc cú pháp và không thay đổi. Không sử dụng API trong các kiểm tra này.

### 3.5. Chạy tác vụ và ghi kết quả (bước 1.3)

Hàm `run_task` tạo thư mục tạm ngoài kho mã nguồn, sao chép workspace và skill tương ứng với điều kiện, rồi dựng tác tử. Sandbox được xóa khi kết thúc bằng `TemporaryDirectory`. Bản ghi gồm thời điểm UTC, mã băm skill trước chạy, thời gian thực thi, token, số lần gọi công cụ, thông điệp cuối và kết quả chấm điểm; được lưu dưới dạng `run.json` cùng vết `trace.md`.

Token được cộng từ `UsageMetadataCallbackHandler`, bao gồm các lần gọi mô hình của subagent. Số lần gọi công cụ và subagent chỉ được đếm trên luồng chính; số skill được đọc là số tên thư mục khác nhau sau `skills/`. Việc sửa skill được phát hiện bằng đối chiếu mã băm trước và sau chạy. Ngoại lệ từ `agent.invoke` được ghi vào `error`, sau đó workspace vẫn được chấm điểm. Theo cách cài đặt tối thiểu trong pseudo-code, khi có ngoại lệ, danh sách message rỗng nên vết rỗng và số lần gọi công cụ bằng 0; hạn chế này cần được lưu ý khi phân tích lần chạy lỗi.

Trước triển khai, `test_03_runner.py` ghi nhận 1 test đạt và 5 test thất bại do TODO. Sau triển khai, 6/6 test đạt trong 2,79 giây. Kiểm tra kết hợp `test_01`, `test_02` và `test_03` đạt 27/27 test trong 9,15 giây trên Linux. Các test xác nhận bản ghi đầy đủ, workspace gốc không bị sửa, lỗi được ghi nhận, thay đổi skill được phát hiện và số đếm phù hợp. Các hàm có sẵn `render_trace`, `main` và cấu hình `CONDITIONS` được đối chiếu với bản gốc và giữ nguyên.

### 3.6. Chạy thử mô hình thật và xác nhận checkpoint Phần 1

Lần chạy `baseline data-learn` bắt đầu lúc `2026-10-06T05:35:36.920957+00:00`, sử dụng giới hạn đệ quy 60. Kết quả đạt 5/8 check, tương ứng điểm 0,625; thời gian 38,7 giây; 76.588 token đầu vào và 2.377 token đầu ra, tổng cộng 78.965 token. Luồng chính có 12 lần gọi công cụ, không giao việc cho subagent và không đọc skill. Bản ghi không có lỗi kết thúc (`error=null`) và không phát hiện thay đổi skill (`skills_modified=false`).

Hai tệp `results/baseline/data-learn/run.json` và `trace.md` đã được kiểm tra; các check thất bại có phản hồi chi tiết. Workspace nguồn trong `tasks/` không thay đổi. Lần chạy này được sử dụng trực tiếp trong Phần 2, theo yêu cầu không chạy lại `data-learn` chỉ để xác nhận đường cơ sở.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Ba tác vụ học được chạy dưới điều kiện `baseline`; kết quả `data-learn` từ Phần 1 được giữ nguyên. Bảng sau bao gồm toàn bộ 15 check thất bại, với sai lệch môi trường được tách khỏi lỗi tác tử.

| Tác vụ | Check thất bại | Nhóm | Bằng chứng từ `detail` hoặc vết |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | Môi trường, loại khỏi taxonomy tác tử | File nguồn CRLF không khớp hash LF của bộ chấm; Git không ghi nhận thay đổi. |
| `code-learn` | `rule_type_hints` | E | “every public function … has type annotations”. |
| `code-learn` | `rule_regression_tests` | E | Thiếu `tests/test_regressions.py` với ít nhất ba test đạt. |
| `code-learn` | `rule_changelog` | E | Thiếu các dòng `- fix(<function name>): …` trong `## Unreleased`. |
| `data-learn` | `rule_money_in_cents` | E | Giá trị tiền phải biểu diễn bằng số nguyên cent. |
| `data-learn` | `rule_meta_block` | E | Thiếu `meta` chứa `source`, `rows_in`, `rows_used`. |
| `data-learn` | `rule_clean_csv` | E | Thiếu `clean.csv` theo schema và định dạng quy định. |
| `logs-learn` | `entry_count` | D; B là yếu tố hỗ trợ | “wrong number of entries (got 14)”. |
| `logs-learn` | `timestamps_utc` | D; B là yếu tố hỗ trợ | “6/25 timestamps match”. |
| `logs-learn` | `exception_fields` | D; B là yếu tố hỗ trợ | “19 wrong `exception` values”. |
| `logs-learn` | `repeat_counts` | D; B là yếu tố hỗ trợ | “19 wrong `repeat_count` values”. |
| `logs-learn` | `counts_by_service` | D; B là yếu tố hỗ trợ | “counts_by_service: wrong values”. |
| `logs-learn` | `rule_service_names` | E | Tên dịch vụ phải viết thường, thay `-` bằng `_`. |
| `logs-learn` | `rule_sorted_errors` | E | Danh sách lỗi phải sắp theo dịch vụ rồi thời gian UTC. |
| `logs-learn` | `rule_schema_header` | E | Thiếu `schema_version=2`, `generated_by=log-triage`. |

Nhóm E chiếm 9/14 lỗi sau khi loại sai lệch môi trường, tương ứng 64,29%; năm lỗi còn lại thuộc xử lý dữ liệu hoặc định dạng (D). Vết logs có hai lần đọc log, một lần ghi JSON và không có lệnh kiểm chứng, hỗ trợ nhận định về thiếu kiểm chứng (B); tác tử không đọc `README.md`, cho thấy thiếu khảo sát đặc tả (A). Việc đọc trực tiếp rồi tổng hợp JSON không bảo đảm tính đầy đủ, chuyển đổi múi giờ và gắn traceback đúng sự kiện. Đây là phân tích từ vết và check; không suy diễn rằng mọi check thất bại là lỗi độc lập.

Bằng chứng phủ định: code đạt 6/7 check kỹ thuật và data đạt 5/5; các hàm code dùng chung và hành vi docstring được bộ chấm xác nhận. Vì vậy, không có căn cứ coi vá triệu chứng (C) là nguyên nhân phổ biến. Logs chỉ đạt 1/6 check kỹ thuật. Toàn bộ baseline đạt 12/18 check kỹ thuật và 0/9 check quy ước; chưa có bằng chứng để quy lỗi không tạo tệp cho nhóm F.

Skill tổng quát có thể hỗ trợ kiểm tra quy ước đầu ra, tính đầy đủ của tệp, xử lý log bằng script và đối chiếu kết quả trước khi kết thúc. Hiệu quả thực tế chưa được xác minh trước Phần 3–4.

Sai lệch CRLF được xác định trên `tasks/code-learn/workspace/tests/test_report.py`: SHA-256 của bản checkout là `efb5e7650d4f03356e8353d209fbcfe81505ce2fd648bd558d5ada6e8b92ff19`; hash khi chuẩn hóa CRLF thành LF và hash trong Git HEAD đều là `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d`, trùng giá trị bộ chấm. File có 32 chuỗi CRLF. Không sửa file hoặc điểm trong `run.json`; giữ điểm thô và ghi hạn chế này khi diễn giải.

Vết data còn ghi hai lỗi đường dẫn tuyệt đối trong shell và lỗi thiếu `pytz`; tác tử tự khắc phục, sau đó cả năm check kỹ thuật đạt. Những sự kiện này làm phát sinh chi phí nhưng không được tính thêm là check thất bại cuối cùng.

## 5. Điều kiện `subagents` (Phần 2.3)

### 5.1. Thiết kế subagent (bước 1.1)

Hàm `get_subagents` định nghĩa ba vai trò theo `guides/pseudocode/02_subagents.md`.

| Subagent | Điều kiện giao việc | Phạm vi và đầu ra |
|---|---|---|
| `explorer` | Cần xác định đặc tả, quan hệ giữa mã nguồn hoặc định dạng dữ liệu trước khi thực hiện | Đọc tài liệu, mã và dữ liệu; không sửa tệp; báo cáo bằng chứng, trường hợp biên và đề xuất. |
| `implementer` | Thay đổi đã xác định hoặc xử lý dữ liệu cần nhiều bước | Thực hiện trong phạm vi được giao; kiểm chứng bằng test hoặc script; báo cáo tệp đã sửa và kết quả thực tế. |
| `reviewer` | Kết quả cần đối chiếu độc lập với yêu cầu và trường hợp biên | Không sửa tệp; kiểm tra đầu ra và báo cáo phát hiện có bằng chứng. |

Phân tách khảo sát, thực hiện và kiểm tra nhằm làm rõ trách nhiệm của từng vai trò. Mỗi subagent có tên duy nhất, `description` nêu điều kiện gọi và `system_prompt` quy định phạm vi. Prompt yêu cầu phân biệt dữ kiện đã xác minh với thông tin còn thiếu do ngữ cảnh được cô lập. Không bổ sung skill cho subagent; quy ước đường dẫn sẽ được nối trong `build_agent` ở bước 1.2.

Tại checkpoint bước 1.1, lệnh `pytest tests/test_02_agent.py -k subagents` ghi nhận 1 test đạt và 2 test thất bại do `build_agent` chưa triển khai. Test riêng `test_subagents_have_required_fields` trong container Linux đạt trong 0,13 giây. Sau bước 1.2, toàn bộ 9 test trong `test_02_agent.py` đạt, xác nhận cả cấu trúc và tích hợp subagent.

### 5.2. Quan sát thực nghiệm (Phần 2.3)

Cả ba lần chạy `subagents` đều giao việc cho `implementer` đúng một lần; `explorer`, `reviewer` và `general-purpose` không xuất hiện trong các lệnh giao việc của luồng chính. Việc phân vai đã kích hoạt giao việc, nhưng chưa kích hoạt kiểm tra độc lập bằng `reviewer`.

| Tác vụ | Thông tin giao việc và kiểm chứng | Kết quả quan sát |
|---|---|---|
| `code-learn` | Giao sửa ba mô-đun theo docstring, cấm sửa test; không truyền đầy đủ đường dẫn `workspace/...` và nội dung đặc tả từng hàm. Tác tử chính ghi lại ba tệp từ báo cáo, không chạy lại test. | Báo cáo subagent nêu lỗi import; tác tử chính vẫn khẳng định test đạt. Bộ chấm báo `visible_suite_passes`: “1 error in 0.09s”. Chi tiết nguyên nhân import chưa thể xác minh vì vết nội bộ không được lưu. |
| `data-learn` | Giao đủ tên chỉ số, miền thời gian và quy tắc thiếu tiền, nhưng đổi khóa khử trùng thành cả bốn cột thay vì giữ một dòng mỗi `order_id`. Tác tử chính đọc lại JSON, không tính lại chỉ số. | `duplicate_rows_removed` nhận 8 thay vì 7; bốn check kỹ thuật khác đạt. Lời giao việc sai đặc tả và không kiểm chứng độc lập là bằng chứng cho A/B, với biểu hiện D ở đầu ra. |
| `logs-learn` | Giao lọc mức log, UTC, exception và thống kê; không truyền schema JSON mẫu, chỉ nói “specified JSON structure”; quy tắc cộng `1 + sum(N)` được rút gọn. Không đọc lại tệp hoặc chạy check. | Cấu trúc đầu ra không đạt, nhiều check báo `KeyError: 'errors'`; tác tử chính dựa vào lời báo hoàn thành của subagent. Đây là lỗi D có liên hệ với thiếu ngữ cảnh và kiểm chứng (A/B). |

Ba check quy ước code và data đều không đạt. Ở logs-subagents, các check `rule_service_names`, `rule_sorted_errors` báo `KeyError: 'errors'`, nên chưa đủ bằng chứng kết luận tác tử đã áp dụng sai từng quy ước đó: sai schema gây lỗi dây chuyền. Check `rule_schema_header` xác nhận thiếu thông tin header. Không coi lời báo hoàn thành là bằng chứng tệp không tồn tại; bộ chấm chỉ xác nhận cấu trúc không đạt.

Trong cả hai điều kiện, check `tests_not_modified` của code không đạt; sai lệch CRLF đã có trước tác tử. Riêng subagent code tự báo từng sửa rồi hoàn nguyên import, nhưng vết không cho thấy thao tác nội bộ. Vì vậy không thể quy toàn bộ thất bại hash của lần này cho CRLF hoặc xác nhận test cuối giữ nguyên byte; cần bảo lưu bất định thay vì kết luận tác tử vi phạm chỉ từ check đó.

Token và thời gian được tổng hợp tại mục 7. Cả sáu lần chạy có `error=null`, `skills_modified=false`, `skills_read=0`. Không có kết quả tác vụ đánh giá ở giai đoạn này.

## 6. Self-evolving: skill do curator sinh (Phần 3)

### 6.1. Triển khai và kiểm tra (Phần 3.1)

Hàm `curate_skills` chỉ sử dụng bản ghi `role=learn` trong điều kiện nguồn; bản ghi đánh giá được bỏ qua trước khi đọc vết. Prompt chứa tên và `detail` của check thất bại cùng tối đa 6.000 ký tự cuối của mỗi vết. Khi không có check thất bại, hàm trả danh sách rỗng và không gọi mô hình. Mô hình được gọi một lần; các khối skill được tách và kiểm tra bằng hàm có sẵn trước khi ghi, tối đa ba skill.

Hai test curator thất bại trước triển khai, sau đó đạt; kiểm tra kết hợp với các hàm có sẵn đạt 14/14 test trong 6,20 giây. Kiểm tra cuối toàn bộ bốn bộ test đạt 29/29 trong 7,54 giây. `validate_skill`, `parse_skill_blocks` và các tệp được bảo vệ giữ nguyên. Test xác nhận loại dữ liệu đánh giá khỏi prompt, đưa phản hồi học vào prompt, từ chối tên đường dẫn không an toàn và không gọi mô hình khi thiếu thất bại.

### 6.2. Sinh và đánh giá skill (Phần 3.2–3.3)

Curator được chạy một lần từ ba kết quả baseline học và ghi hai skill hợp lệ. Không xóa skill, không chạy lại curator, không sửa tay nội dung. Nội dung phản hồi vẫn có check hash chịu sai lệch CRLF; prompt yêu cầu phân biệt sai lệch môi trường với hành vi sửa tệp, nhưng chỉ dẫn này không đảm bảo curator suy luận đúng.

| Skill | Tính tổng quát và đúng đắn | Độ dài và tình huống kích hoạt | Quyết định |
|---|---|---|---|
| `preserve-original-test-files` | Quy trình bảo toàn test gốc, thêm test trong tệp mới và kiểm chứng bằng diff; phù hợp ràng buộc tác vụ code. Không chứa tên dữ liệu hoặc đáp án. Có bước sao lưu và rà soát lặp lại; không khắc phục trực tiếp sai lệch CRLF. | 14 dòng toàn tệp, 10 dòng thân; `Use when modifying or adding tests …` rõ nhưng thiên về công việc test. | Giữ nguyên; chưa có dấu hiệu hướng dẫn gây hại trong phạm vi tác vụ. |
| `enforce-type-annotations-on-public-functions` | Yêu cầu tham số và kiểu trả về của hàm public có annotation, khớp `rule_type_hints`. Có ví dụ hàm minh họa tổng quát, không phải hàm riêng của workspace. `mypy` là kiểm chứng bổ sung, có thể phát sinh chi phí hoặc thiếu công cụ. | 14 dòng toàn tệp, 10 dòng thân; `Use when writing or updating package code …` phù hợp miền code. | Giữ nguyên; hạn chế là chưa bao phủ quy ước data/logs, regression test và changelog. |

Các skill đạt `validate_skill`, không chứa định danh tác vụ đánh giá theo bộ kiểm tra. Điều này xác nhận điều kiện kỹ thuật, không chứng minh khả năng khái quát hóa. Mã băm từng tệp được lưu trong `report/phase3_skill_manifest.json` và được đối chiếu sau thí nghiệm; byte của cả hai tệp không đổi.

### 6.3. Kiểm tra sử dụng trên tập học (Phần 3.4)

Ba lần chạy `skills-auto` dùng cùng mã băm skill ban đầu `5a039da97ce7b0bdfaaf4000535ada94fe1db0884791e4d3bcdf68755de75b0b` và đều có `skills_modified=false`, `error=null`.

| Tác vụ | Check đạt | Token | Thời gian (s) | `skills_read` | Bằng chứng và đối chiếu |
|---|---:|---:|---:|---:|---|
| `code-learn` | 5/10 | 97.857 | 31,0 | 0 | Không có lệnh đọc skill. Test nhìn thấy đạt sau sửa `PYTHONPATH`, nhưng check CSV quoting và ba check quy ước không đạt; `rule_type_hints` không được cải thiện. |
| `data-learn` | 5/8 | 49.691 | 19,9 | 0 | Không đọc skill; năm check kỹ thuật đạt, ba check quy ước không đạt, giống baseline về điểm. |
| `logs-learn` | 1/9 | 27.654 | 15,6 | 0 | Không đọc skill, viết JSON trực tiếp; cấu trúc đạt nhưng số sự kiện, UTC, exception, repeat count và quy ước chưa đạt. |

Vết cả ba tác vụ không có lệnh đọc `SKILL.md`. Ở code, không thấy bổ sung type hint hoặc thực hiện checklist của skill. Việc không sửa test trong luồng chính phù hợp quy tắc sẵn có của đề, nên không thể gán cho skill chưa được đọc. Ở data/logs, mô tả hai skill thiên về code có thể không phù hợp; riêng code, nguyên nhân bỏ qua skill chưa xác định dù prompt có chỉ dẫn đọc trước. Do đó, chưa có bằng chứng skill được thực thi hoặc tạo cải thiện nhân quả.

Kết quả Phần 3.4 được sao lưu nguyên trạng vào `results/skills-auto-dev/`, giữ cả bản hiện hành trong `results/skills-auto/`. Bản sao sẽ dùng để đối chiếu các lần chạy sau đóng băng ở Phần 4; hiện chưa tạo tag `freeze` hoặc chạy tác vụ đánh giá.

## 7. Kết quả so sánh (sơ bộ trước đóng băng)

Bảng đầu ghi kết quả Phần 2; kết quả skills-auto trước đóng băng được trình bày ở mục 6.3 và bảng tổng hợp dưới đây. Bảng chính thức ba điều kiện và sáu tác vụ sẽ được tạo ở Phần 4 từ `lab.compare`.

| Tác vụ | Baseline: check đạt | Subagents: check đạt | Token baseline | Token subagents | Thời gian baseline (s) | Thời gian subagents (s) |
|---|---:|---:|---:|---:|---:|---:|
| `code-learn` | 6/10 | 5/10 | 23.993 | 80.620 | 12,8 | 48,2 |
| `data-learn` | 5/8 | 4/8 | 78.965 | 75.481 | 38,7 | 34,9 |
| `logs-learn` | 1/9 | 0/9 | 20.504 | 53.219 | 13,7 | 30,8 |
| Điểm trung bình theo tác vụ | 44,54% | 33,33% | — | — | — | — |
| Trung bình token/thời gian | — | — | 41.154 | 69.773,33 | 21,73 | 37,97 |
| Tổng token | — | — | 123.462 | 209.320 | — | — |

Thống kê từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    12/18         0/9           41,154      0/3
subagents     learn     9/18         0/9           69,773      0/3
skills-auto   learn    11/18         0/9           58,400      0/3
(evaluation rows are hidden until the git tag `freeze` exists)
```

Công cụ thống kê làm tròn xuống token trung bình. Các điểm được giữ nguyên từ bộ chấm, gồm check hash chịu ảnh hưởng CRLF; không điều chỉnh để cải thiện kết quả.

Tổng hợp ba điều kiện trên tập học, trước đóng băng:

| Điều kiện | Điểm trung bình | Check kỹ thuật | Check quy ước | Token trung bình | Tổng token | Thời gian trung bình (s) |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 44,54% | 12/18 | 0/9 | 41.154 | 123.462 | 21,73 |
| Subagents | 33,33% | 9/18 | 0/9 | 69.773,33 | 209.320 | 37,97 |
| Skills-auto (Phần 3.4) | 41,20% | 11/18 | 0/9 | 58.400,67 | 175.202 | 22,17 |

## 8. Phân tích

Trên ba tác vụ học, subagents giảm điểm trung bình 11,20 điểm phần trăm so với baseline, trong khi tăng token tổng khoảng 69,54% và thời gian trung bình khoảng 74,69%. Riêng data dùng ít token hơn 4,41% nhưng giảm một check đạt. Hai tác vụ còn lại tăng chi phí và giảm điểm. Với dữ liệu hiện tại, đa tác tử chưa thể hiện lợi ích tương xứng chi phí.

Vết cho thấy lời giao việc thiếu hoặc biến đổi đặc tả, cùng việc tác tử chính không kiểm tra độc lập báo cáo subagent. Các thất bại quy ước chiếm đa số trong baseline, tạo cơ sở cho curator sinh hướng dẫn về schema, quy ước và kiểm chứng. Phần 3 đã sinh hai skill nhưng không có lần đọc nào trong ba vết. Skills-auto giảm điểm trung bình 3,33 điểm phần trăm và tăng token khoảng 41,91% so với baseline; chưa thể quy chênh lệch cho nội dung skill do không có bằng chứng đọc và chỉ chạy một lần. Cả ba điều kiện đều chưa đạt check quy ước nào. Không có check cụ thể được chứng minh là cải thiện nhờ skill; `rule_type_hints` là ví dụ skill phù hợp nhưng chưa được đọc, còn quy ước data/logs nằm ngoài nội dung skill. Khả năng khái quát, quá khớp và nhiễu sau đóng băng sẽ được đánh giá ở Phần 4.

## 9. Hạn chế và tính hợp lệ

1. Mỗi điều kiện chỉ chạy một lần trên ba tác vụ học, nên chênh lệch có thể chịu ảnh hưởng nhiễu; chưa đủ để khẳng định hiệu quả ổn định hoặc tổng quát hóa.
2. Thí nghiệm chỉ sử dụng `gpt-4.1-mini` và các tác vụ có quy ước Acme; kết quả chưa đại diện cho mô hình hoặc miền tác vụ khác.
3. Vết chỉ chứa luồng chính. Không quan sát trực tiếp thao tác và kiểm chứng nội bộ subagent; lời báo cáo của subagent không thay thế bằng chứng thực thi.
4. Sai lệch CRLF của file test code làm check bảo toàn test thất bại trước khi tác tử chạy, gây nhiễu điểm thô. Kết quả được giữ nguyên và ghi rõ giới hạn diễn giải.
5. Token được cộng đầy đủ nhưng số lần gọi công cụ chỉ đếm ở luồng chính, nên không dùng số đếm này để suy ra toàn bộ công việc subagent. Curator đã thực hiện một lần, nhưng token của lượt sinh skill chưa được đo; tác vụ đánh giá và kiểm tra đóng băng chưa thực hiện.

## 10. Kết luận

Phần 0–3 đã hoàn thành với 29/29 test ngoại tuyến đạt, chín bản ghi tác vụ học và hai skill do curator sinh. Trên tập học, baseline đạt điểm trung bình 44,54%, skills-auto 41,20% và subagents 33,33%. Không có lần đọc skill được ghi nhận, nên chưa có bằng chứng skill tự sinh được thực thi hoặc cải thiện kết quả. Kết luận giới hạn ở các lần chạy quan sát, chịu ảnh hưởng của nhiễu và sai lệch CRLF. Bước tiếp theo là viết giả thuyết, đóng băng skill và đánh giá theo Phần 4.

## Phụ lục

Kiểm thử lại sau Phần 3: bốn bộ test đạt `29 passed in 8.19s`. Mô hình giả xác nhận hai skill và chỉ dẫn đọc trước có trong system prompt. Check bảo toàn test code thất bại ngay trên workspace chưa bị tác tử sửa, do sai lệch CRLF đã xác định. Hash skill khác giữa Windows và Linux vì cách biểu diễn đường dẫn; công cụ đóng băng cần chạy cùng môi trường Linux với runner. Image hiện chưa có Git, cần bổ sung trước Phần 4. Phát hiện, bằng chứng và phương hướng xử lý được ghi trong `report/RECHECK.md`; không sửa mã nguồn, skill hoặc kết quả chạy trong lượt kiểm tra này.

Các lệnh kiểm tra chính, theo trình tự thực hiện:

```powershell
python -m pytest tests/test_01_provided.py --basetemp=<thu_muc_tam_rieng>
python scripts/tour.py
```

Kiểm tra kết nối mô hình trên máy chủ:

```powershell
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
```

Chuẩn bị và kiểm tra môi trường Linux:

```powershell
docker build -t lab-deepagents .
docker run --rm --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" lab-deepagents python -m pytest tests/test_01_provided.py
```

Kiểm tra `/bin/sh` và kết nối mô hình trong container được thực hiện bằng `docker run --rm --env-file .env lab-deepagents python -c ...`. Thử thách mở rộng chưa thực hiện.

Kiểm tra bước 1.1, trước và sau triển khai:

```powershell
python -m pytest tests/test_02_agent.py -k subagents --tb=short
docker run --rm --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" lab-deepagents python -m pytest tests/test_02_agent.py::test_subagents_have_required_fields
```

Phạm vi sửa mã nguồn: chỉ thân hàm TODO `get_subagents` trong `src/lab/subagents.py`. Các tệp có sẵn, hằng số prompt và thư mục `tests/`, `tasks/`, `scripts/` được giữ nguyên.

Bước 1.2 bổ sung các import cần thiết và triển khai hai hàm TODO `make_backend`, `build_agent` trong `src/lab/agent.py`. Lệnh sau được chạy trước và sau triển khai:

```powershell
docker run --rm --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" lab-deepagents python -m pytest tests/test_02_agent.py --tb=short
```

Bước 1.3 bổ sung các import cần thiết và triển khai hàm TODO `run_task` trong `src/lab/runner.py`. Hai lệnh kiểm tra chính:

```powershell
docker run --rm --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" lab-deepagents python -m pytest tests/test_03_runner.py --tb=short
docker run --rm --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" lab-deepagents python -m pytest tests/test_01_provided.py tests/test_02_agent.py tests/test_03_runner.py
```

Lần chạy mô hình thật của Phần 1 sử dụng repo chỉ đọc và gắn riêng thư mục kết quả có quyền ghi:

```powershell
docker run --rm --env-file .env --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539,target=/lab,readonly" --mount "type=bind,source=E:\vcode\track3\K4-DAY20-MULTIAGENTS-BuiTienCuong-2A202602539\results,target=/lab/results" lab-deepagents python -m lab.runner --condition baseline --tasks data-learn --recursion-limit 60
```

Phần 2 chạy tuần tự trong container với cùng các tham số mount và `--env-file .env` của Phần 1; lệnh bên trong container:

```bash
python -m lab.runner --condition baseline --tasks code-learn logs-learn --recursion-limit 60
python -m lab.runner --condition subagents --tasks learn --recursion-limit 60
```

Thống kê được chạy trên Windows bằng `python scripts/check_breakdown.py`. Đã kiểm tra đủ sáu cặp `run.json`/`trace.md`, tính nhất quán token, điểm và phản hồi thất bại; không sửa nguồn trong `tasks/`, `tests/`, `scripts/`. Không chạy lại baseline data, không chạy tác vụ đánh giá, không sửa skill.

Phần 3 thực hiện theo thứ tự:

```bash
python -m pytest tests/test_01_provided.py tests/test_04_curator.py
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 60
python -m pytest tests/test_01_provided.py tests/test_02_agent.py tests/test_03_runner.py tests/test_04_curator.py
```

Các lệnh chạy trong container Linux. Curator dùng `.env`, gắn repo chỉ đọc và gắn riêng `skills/auto` để ghi đầu ra. Runner dùng repo và skill chỉ đọc, gắn riêng `results` để ghi kết quả. Kết quả Phần 3.4 được sao chép sang `results/skills-auto-dev`, xác nhận từng tệp có byte giống bản gốc. Không sửa tay skill, không chạy lại curator, không chỉnh điểm hoặc phản hồi trong bản ghi.

Phần 4 giữ nguyên bản checkout và cấu hình tác tử đã dùng ở Phần 2–3 để tránh thay đổi môi trường giữa các điều kiện. Sai lệch CRLF được bảo lưu và diễn giải như hạn chế; không sửa file tác vụ hoặc điểm. Việc tạo bản làm việc LF để đo lại được dành cho thí nghiệm bổ sung.
