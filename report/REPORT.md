# Báo cáo Lab: Self evolving Agentic

Bài thực hành khảo sát chất lượng và chi phí của ba cấu hình tác tử: baseline, subagents và skills-auto. Tôi thực hiện cá nhân theo `GUIDE.md`, bao gồm thí nghiệm chính thức và mở rộng 6e nhằm đo biến động giữa các lần chạy.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Bùi Tiến Cường | 2A202602539 | Toàn bộ triển khai, thực nghiệm, phân tích và báo cáo. |

| Thành phần | Cấu hình |
|---|---|
| Mô hình | `gpt-4.1-mini`, endpoint `https://api.openai.com/v1` |
| Tham số | Nhiệt độ 0; `recursion_limit=60` |
| Thư viện và môi trường | Deep Agents 0.7.21; Windows/Python 3.11.9; thực nghiệm trong Docker Linux/Python 3.12.15 |
| Image | `lab-deepagents:latest` |
| Số lần chạy | 18 chính thức, 3 phát triển trước đóng băng, 18 mở rộng |
| Chi phí | 938.677 token chính thức; 937.151 token mở rộng; tổng runner 2.051.030 token, chưa gồm curator và kiểm tra kết nối; chưa xác định ngân sách tiền |
| Commit giả thuyết | `e38b9396ec6e76ff2622ddf5bc466033b08d31dc` |
| Tag `freeze` | `809f4c69ad5d7befbfa0a54484f29968cde97d9d`, 06/10/2026 lúc 17:12:21 UTC+7 |

Các hàm TODO trong bốn mô-đun được triển khai theo hướng dẫn; tệp và hằng số được bảo vệ giữ nguyên. Khóa API lưu trong `.env`, không đưa vào Git hoặc môi trường shell của tác tử. Lần kiểm thử gần nhất đạt 29/29 test trong 8,12 giây.

## 2. Giả thuyết (Phần 4.0)

Các giả thuyết dưới đây được lập sau Phần 3, trước khi chạy hoặc xem điểm tác vụ đánh giá. Căn cứ gồm số liệu tập học, vết thực thi và lưu ý khoa học trong `guides/pseudocode/04_curator.md` về việc lợi ích trên tập học có thể không chuyển sang tác vụ mới. Đây là dự đoán cần kiểm chứng, không phải kết luận về tập đánh giá.

- H1 (subagents so với baseline): Dự đoán baseline có điểm đánh giá trung bình cao hơn subagents và dùng ít token hơn. Trên tập học, baseline đạt 44,54% so với 33,33%, trong khi subagents tăng token 69,54%; vết cho thấy thiếu hoặc biến đổi đặc tả khi giao việc và thiếu kiểm chứng đầu ra. Việc thêm subagent chưa bảo đảm cải thiện chất lượng.
- H2 (skills-auto so với baseline): Dự đoán skills-auto không cải thiện điểm đánh giá trung bình so với baseline; baseline được dự đoán là điều kiện tốt nhất. Hai skill tập trung miền code, chưa bao phủ quy ước data/logs và không được đọc trong cả ba lần chạy học; điểm học skills-auto đạt 41,20%, thấp hơn baseline. Nếu skill được đọc ở tập đánh giá, lợi ích dự kiến tập trung ở quy ước type hint chứ không bao phủ mọi check mới.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình đánh giá của skills-auto thấp hơn điểm học sau đóng băng, và hiệu quả học không chuyển đầy đủ sang dữ liệu mới. GUIDE nêu tác vụ đánh giá thêm quy ước mới; skill hiện có phạm vi hẹp. Chênh lệch giữa lần học trước và sau đóng băng của cùng bộ skill sẽ được dùng làm dấu hiệu nhiễu, không diễn giải toàn bộ thành hiệu quả học.

## 3. Làm quen Deep Agents (Phần 0.3)

Quan sát từ `scripts/tour.py` sử dụng mô hình giả:

1. Chín công cụ gồm `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`; `execute` thực thi lệnh shell.
2. `task` tạo subagent tạm thời. `general-purpose` hỗ trợ công việc nhiều bước bằng cùng tập công cụ; mặc định chỉ nhận prompt giao việc, không nhận toàn bộ lịch sử tác tử chính. Vì vậy, lời giao việc cần đủ đặc tả và đường dẫn.
3. System prompt mặc định rỗng, nhưng mô tả công cụ vẫn hướng dẫn hành vi: `task` yêu cầu “The agent's report is not shown to the user; relay a summary yourself.”; `execute` yêu cầu “Quote paths containing spaces (e.g. cd "/path/with spaces").”.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Bảng dưới liệt kê 15 check thất bại của baseline trên tập học. Nhóm E là vi phạm quy ước; D là xử lý dữ liệu/định dạng; B là thiếu kiểm chứng.

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

Sau khi loại sai lệch môi trường, E chiếm 9/14 lỗi (64,29%); năm lỗi còn lại thuộc D. Vết logs không đọc `README.md` và không kiểm chứng JSON, cho thấy thiếu khảo sát đặc tả và xác minh đầu ra. Skill về quy ước và kiểm chứng có thể hỗ trợ, nhưng hiệu quả cần được thực nghiệm xác nhận.

Baseline đạt 12/18 check kỹ thuật: code 6/7, data 5/5, logs 1/6; đồng thời đạt 0/9 check quy ước. Kết quả chưa hỗ trợ nhận định vá triệu chứng hoặc báo tạo tệp không tồn tại là lỗi phổ biến.

Check bảo toàn test code-learn thất bại ngay trên workspace chưa chạy tác tử do CRLF khác LF kỳ vọng. Tệp có 32 chuỗi CRLF; SHA-256 bản checkout là `efb5e7650d4f03356e8353d209fbcfe81505ce2fd648bd558d5ada6e8b92ff19`, còn bản chuẩn hóa LF và bản Git là `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d`. Tôi giữ nguyên tệp và điểm thô; riêng subagents thiếu vết nội bộ nên không quy toàn bộ lỗi hash cho CRLF.

## 5. Điều kiện `subagents` (Phần 2.3)

| Vai trò | Điều kiện gọi và phạm vi |
|---|---|
| `explorer` | Khảo sát đặc tả trước triển khai; đọc, không sửa tệp; báo bằng chứng và trường hợp biên. |
| `implementer` | Thực hiện thay đổi đã xác định; kiểm chứng và báo kết quả thực tế. |
| `reviewer` | Kiểm tra độc lập sau triển khai; không sửa tệp; báo sai lệch so với yêu cầu. |

Thiết kế phân tách khảo sát, thực hiện và kiểm tra; prompt quy định phạm vi và đường dẫn cho từng vai trò.

| Tác vụ | `subagent_calls` | Quan sát từ vết/kết quả |
|---|---:|---|
| code-learn | 1 | Giao `implementer` nhưng thiếu đặc tả/đường dẫn đầy đủ; tác tử chính không chạy lại test. Subagent báo lỗi import, thông điệp cuối vẫn khẳng định test đạt; bộ chấm ghi một lỗi test. |
| data-learn | 1 | Khử trùng được giao theo bốn cột thay vì `order_id`; `duplicate_rows_removed=8`, kỳ vọng 7; thiếu tính lại chỉ số. |
| logs-learn | 1 | Thiếu schema JSON và rút gọn quy tắc repeat khi giao việc; nhiều check báo `KeyError: 'errors'`. |
| code-eval | 0 | Không giao việc; đạt 6/11. |
| data-eval | 1 | Có giao việc; đạt 3/9. |
| logs-eval | 1 | Có giao việc; đạt 1/10. |

Trên tập học, chỉ `implementer` được gọi; `explorer` và `reviewer` không được sử dụng. Token trung bình tăng từ 41.154 lên 69.773,33 (+69,54%); thời gian tăng từ 21,73 lên 37,97 giây (+74,69%). Trên đánh giá, token tăng từ 35.056,33 lên 64.764,33; thời gian từ 19,17 lên 21,53 giây. Thiếu ngữ cảnh và kiểm chứng là cơ chế khả dĩ, chưa đủ xác định nguyên nhân từng thất bại đánh giá.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator chạy một lần từ ba bản ghi baseline học, sinh hai skill; không xóa, sửa tay hoặc chạy lại. Chỉ dữ liệu học được đưa vào prompt; skill được kiểm tra trước khi ghi. Khi không có check thất bại, curator không gọi mô hình.

| Skill | Tính tổng quát và đúng đắn | Độ dài, mô tả kích hoạt và sử dụng Phần 3.4 |
|---|---|---|
| `preserve-original-test-files` | Quy trình tổng quát bảo toàn test và bổ sung test mới, phù hợp ràng buộc code; không giải quyết trực tiếp CRLF. | 14 dòng, 10 dòng thân; “Use when modifying or adding tests …”; không được đọc trong ba tác vụ. |
| `enforce-type-annotations-on-public-functions` | Hướng dẫn annotation hàm public phù hợp `rule_type_hints`; `mypy` có thể thiếu hoặc phát sinh chi phí; chưa bao phủ quy ước data/logs. | 14 dòng, 10 dòng thân; “Use when writing or updating package code …”; không được đọc trong ba tác vụ. |

Hai skill hợp lệ và giữ nguyên hash. Vết không có lệnh đọc `SKILL.md`; code không bổ sung annotation. Mô hình giả xác nhận skill và chỉ dẫn đọc trước đã có trong system prompt, nhưng nguyên nhân tác tử bỏ qua chưa xác định. Kết quả Phần 3.4 được giữ tại `results/skills-auto-dev/`; dữ liệu sau đóng băng nằm tại `results/skills-auto/`.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Giả thuyết được commit trước tag `freeze`; các lần đánh giá và skills-auto chính thức bắt đầu sau đóng băng. Công cụ kiểm tra trả `checked 6 runs of skill conditions: OK`. Cả 18 bản ghi chính thức có `error=null`, `skills_modified=false`; phản hồi chi tiết đánh giá được ẩn theo giao thức.

Bảng nguyên bản từ `python -m lab.compare`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 5/10 | 6/10 |
| data-learn | 5/8 | 4/8 | 5/8 |
| logs-learn | 1/9 | 0/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 5/9 | 3/9 | 5/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.45 | 0.33 | 0.45 |
| **Mean score - evaluation tasks** | 0.40 | 0.33 | 0.40 |
| **Mean tokens per run** | 38,105 | 67,268 | 51,072 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Thống kê từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     12/18         0/12          35,056      0/3
baseline      learn    12/18         0/9           41,154      0/3
subagents     eval     10/18         0/12          64,764      0/3
subagents     learn     9/18         0/9           69,773      0/3
skills-auto   eval     12/18         0/12          59,358      0/3
skills-auto   learn    12/18         0/9           42,786      0/3
```

Điểm trung bình được tính theo tác vụ. Bảng công cụ làm tròn điểm và cắt phần lẻ token; mục phân tích sử dụng số chưa làm tròn.

## 8. Phân tích

1. **Chất lượng và giả thuyết.** Trên tập học, baseline và skills-auto cùng đạt 44,54%, subagents đạt 33,33%; trên đánh giá tương ứng 40,03%, 40,03% và 32,63%. Không điều kiện bổ sung nào cải thiện so với baseline. H1 phù hợp quan sát; H2 phù hợp dự đoán không cải thiện nhưng baseline chỉ đồng hạng tốt nhất. H3 đúng về chiều giảm 4,50 điểm phần trăm, chưa đủ chứng minh quá khớp.

2. **Kỹ thuật và quy ước.** Baseline/skills-auto cùng đạt 12/18 check kỹ thuật ở mỗi tập; subagents đạt 9/18 trên học và 10/18 trên đánh giá. Mỗi điều kiện đạt 0/9 check quy ước học và 0/12 check quy ước đánh giá. Chưa có bằng chứng skill hỗ trợ nhóm check hoặc quy ước mới, do phạm vi hẹp và không được đọc.

3. **Sử dụng skill.** Không có check đạt nhờ skill được dữ liệu chứng minh. CSV quoting của code-learn chuyển sang đạt sau đóng băng, nhưng skill không đổi và `skills_read=0`, nên không quy cải thiện cho skill. `rule_type_hints` vẫn không đạt dù skill phù hợp, cho thấy hướng dẫn chưa được thực thi.

4. **Chi phí.** Token trung bình trên sáu tác vụ là 38.105,17; 67.268,83; 51.072,17, tương ứng baseline, subagents, skills-auto. Điểm đánh giá trên mỗi 1.000 token lần lượt là 0,01142; 0,00504; 0,00674 ở thang điểm 0–1. Baseline có hiệu quả cao nhất; subagents chưa thể hiện lợi ích tương xứng chi phí trong thí nghiệm này.

5. **Rò rỉ và quá khớp.** Curator chỉ nhận dữ liệu học; skill không chứa định danh đánh giá theo bộ kiểm tra và không đổi sau đóng băng. Chưa thấy dấu hiệu rò rỉ trong phạm vi kiểm tra. Điểm học cao hơn đánh giá chưa đủ kết luận quá khớp khi skill chưa được đọc và mẫu nhỏ.

6. **Nhiễu.** Skills-auto trước/sau đóng băng đạt code 5/10→6/10, data 5/8→5/8, logs 1/9→1/9; điểm trung bình tăng 41,20%→44,54% (+3,33 điểm phần trăm). Cùng bộ skill nhưng kết quả thay đổi là dấu hiệu biến động giữa lần chạy, chưa phải hiệu quả học; một cặp lần chạy chưa ước lượng được phân bố nhiễu.

## 9. Hạn chế và tính hợp lệ

1. Ba tác vụ mỗi vai trò, một lần chính thức và ba lượt đánh giá mở rộng: mẫu nhỏ, chưa đủ kiểm định khác biệt hoặc suy rộng.
2. Một mô hình và quy ước Acme do đề thiết kế: kết quả chưa đại diện cho miền hoặc mô hình khác.
3. Vết chỉ có luồng chính: chưa quan sát trực tiếp thao tác nội bộ subagent để xác định nguyên nhân.
4. Sai lệch CRLF gây nhiễu check bảo toàn test code-learn; giữ nguyên checkout và điểm để thống nhất điều kiện.
5. Không có lần đọc skill và chưa đo chi phí curator/tiền: chưa đánh giá được hiệu quả khi skill được tuân thủ hoặc tổng chi phí tài chính.

## 10. Kết luận

Thực nghiệm gồm 18 lần chính thức, hai skill tự sinh và 18 lần lặp bổ sung. Baseline và skills-auto cùng đạt 40,03% trên đánh giá chính thức; subagents đạt 32,63%, tương ứng trung bình 35,34% khi tính ba lượt. Baseline có hiệu quả điểm trên token cao nhất; chưa có bằng chứng skill cải thiện kết quả. Kết luận giới hạn bởi mẫu nhỏ, biến động và sai lệch CRLF. Hướng tiếp theo là đo việc đọc/tuân thủ skill, mở rộng tác vụ và chạy lặp trong môi trường LF thống nhất.

## Phụ lục

### A. Lệnh thực hiện và tái lập

Các lệnh chính dưới đây chạy trong container Linux theo thứ tự; baseline data-learn từ bước chạy thử được giữ lại. Runner gắn repo chỉ đọc và riêng `results` có quyền ghi; curator gắn riêng `skills/auto` để ghi skill.

```bash
python -m pytest tests/test_01_provided.py
python scripts/tour.py
python -m pytest tests/test_02_agent.py
python -m pytest tests/test_03_runner.py
python -m lab.runner --condition baseline --tasks data-learn --recursion-limit 60
python -m lab.runner --condition baseline --tasks code-learn logs-learn --recursion-limit 60
python -m lab.runner --condition subagents --tasks learn --recursion-limit 60
python -m pytest tests/test_01_provided.py tests/test_04_curator.py
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 60
python -m pytest
```

Sau khi sao lưu Phần 3.4, ghi giả thuyết, commit `hypotheses`, commit `freeze skills` và tạo tag `freeze`, chạy:

```bash
python -m lab.runner --condition baseline --tasks eval --recursion-limit 60
python -m lab.runner --condition subagents --tasks eval --recursion-limit 60
python -m lab.runner --condition skills-auto --tasks all --recursion-limit 60
python -m lab.compare
python scripts/check_breakdown.py
```

Mẫu lệnh Docker từ PowerShell tại thư mục gốc repo:

```powershell
$repoPath = (Get-Location).Path
docker build -t lab-deepagents .
docker run --rm --env-file .env --mount "type=bind,source=$repoPath,target=/lab,readonly" --mount "type=bind,source=$repoPath\results,target=/lab/results" lab-deepagents python -m lab.runner --condition baseline --tasks data-learn --recursion-limit 60
docker build -f report/Dockerfile.verify -t lab-deepagents-verify .
docker run --rm -e GIT_CONFIG_COUNT=2 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/lab -e GIT_CONFIG_KEY_1=core.autocrlf -e GIT_CONFIG_VALUE_1=true --mount "type=bind,source=$repoPath,target=/lab,readonly" lab-deepagents-verify python scripts/verify_freeze.py
```

Image kiểm tra chỉ bổ sung Git, không dùng để chạy tác tử. Kiểm tra đóng băng sử dụng Linux để thống nhất biểu diễn đường dẫn khi băm skill. Cấu hình và bằng chứng được lưu trong `report/phase4_protocol.json`, `report/freeze_check.txt`, `report/phase3_skill_manifest.json`.

### B. Mở rộng 6e: lặp để đo nhiễu

Dùng chín lần đánh giá chính thức làm lượt 1; chạy thêm hai lượt mỗi điều kiện trên ba tác vụ (18 lần bổ sung), giữ nguyên cấu hình và chạy tuần tự. Dữ liệu mới lưu tại `results/noise/round-2/`, `round-3/`; thiết kế và lệnh tái lập nằm trong `report/phase6/protocol.json`, `report/phase6/README.md`.

| Điều kiện | Trung bình (%) | Min–max trung bình lượt (%) | SD giữa lượt (điểm %) | Token/lần | Giây/lần | Lần đọc skill |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 40.03 | 40.03–40.03 | 0.00 | 32,609.67 | 17.21 | 0/9 |
| subagents | 35.34 | 32.63–36.70 | 2.35 | 64,106.89 | 22.37 | 0/9 |
| skills-auto | 40.03 | 40.03–40.03 | 0.00 | 60,470.89 | 18.80 | 0/9 |

Trung bình lượt là trung bình ba tác vụ; SD là độ lệch chuẩn mẫu giữa ba lượt theo đơn vị điểm phần trăm. Min–max là khoảng quan sát, không phải khoảng tin cậy. Bảng từng tác vụ lưu tại `report/phase6/table.md`.

Subagents biến động ở data (3/9, 5/9, 5/9) và logs (1/10, 0/10, 0/10). Hai check UTC của data chuyển sang đạt; logs mất check `valid_structure` ở hai lượt bổ sung. Vết cho thấy mỗi tác vụ data/logs giao `implementer` một lần, lời giao việc thay đổi và luồng chính logs không dùng `execute`; thiếu vết nội bộ nên chưa xác định quan hệ nhân quả.

Khoảng cách baseline–subagents giảm từ 7,41 xuống 4,69 điểm phần trăm khi lấy trung bình ba lượt, nhưng thứ hạng không đổi. Baseline/skills-auto đạt 36/54 check kỹ thuật; subagents đạt 32/54; mỗi điều kiện đạt 0/36 check quy ước. Cả 18 lượt bổ sung không có lỗi runtime hoặc sửa skill; tất cả 27 lượt đánh giá không đọc skill. Dữ liệu chính thức và byte skill giữ nguyên, xác nhận bằng bộ tổng hợp ngoại tuyến:

```powershell
python report/phase6/analyze_noise.py
```

Ba lượt trên cùng tác vụ chỉ hỗ trợ thống kê mô tả; SD bằng 0 không chứng minh mô hình không nhiễu. Thứ tự chạy cố định và CRLF tiếp tục hạn chế diễn giải. Thí nghiệm tiếp theo cần nhiều lượt/tác vụ hơn và cân bằng thứ tự chạy.
