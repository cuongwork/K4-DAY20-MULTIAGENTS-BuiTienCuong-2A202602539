# Phần 6e: lặp để đo nhiễu

Câu hỏi: thứ hạng quan sát ở lần đánh giá chính thức có duy trì khi lặp lại không?

- Lượt 1: giữ nguyên chín bản ghi đánh giá tại `results/{condition}/{task}`.
- Lượt 2 và 3: 18 lần bổ sung tại `results/noise/round-{2,3}/{condition}/{task}`.
- Cùng `gpt-4.1-mini`, nhiệt độ 0, recursion limit 60, image `lab-deepagents:latest`, checkout và bộ skill đã đóng băng. Chạy tuần tự theo lượt, rồi baseline/subagents/skills-auto.
- Không sửa nguồn, prompt, skill, tệp tác vụ hoặc kết quả chính thức. `protocol.json` lưu thiết kế và hash trước thí nghiệm; `.env` không được sao chép vào kết quả.

Lệnh chạy từ PowerShell tại thư mục gốc repo:

```powershell
$repoPath = (Get-Location).Path
foreach ($noiseRound in 2,3) {
    foreach ($noiseCondition in "baseline","subagents","skills-auto") {
        docker run --rm --env-file .env --mount "type=bind,source=$repoPath,target=/lab,readonly" --mount "type=bind,source=$repoPath\results,target=/lab/results" lab-deepagents python -m lab.runner --condition $noiseCondition --tasks eval --results "results/noise/round-$noiseRound" --recursion-limit 60
        if ($LASTEXITCODE -ne 0) { throw "Noise run failed" }
    }
}
python report/phase6/analyze_noise.py
```

Không chạy lại lệnh runner nếu chỉ muốn đọc kết quả đã lưu. Bộ tổng hợp không gọi API và chỉ xuất thống kê khi đủ 27 cặp run/trace, gồm chín lần gốc. Nó kiểm tra hash nguồn kết quả và skill, token, điểm, thời điểm sau freeze và phản hồi đánh giá bị ẩn. Các lỗi runtime vẫn được giữ và báo riêng, không bị thay thế âm thầm.

`table.md` báo trung bình/min–max/SD mẫu của ba lần cho từng cặp điều kiện–tác vụ. `aggregate.md` báo trung bình của ba điểm trung bình lượt; khoảng min–max và SD được tính giữa ba lượt, không gộp điểm các miền thành khoảng nhiễu. `summary.json` giữ số chưa làm tròn, token, thời gian, sử dụng skill/subagent và check kỹ thuật/quy ước. SD dùng mẫu số n−1; khoảng dao động không phải khoảng tin cậy. Với ba lượt và ba tác vụ cố định, chỉ diễn giải mô tả, không khẳng định ý nghĩa thống kê hoặc đại diện cho tác vụ mới.
