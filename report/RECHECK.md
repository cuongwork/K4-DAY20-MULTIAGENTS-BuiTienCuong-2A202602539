# Kiểm thử lại và hướng xử lý sau Phần 3

Ngày kiểm tra: 06/10/2026. Phạm vi: kiểm thử ngoại tuyến, tái hiện lỗi môi trường và phân tích vết đã có. Không gọi API, không sửa skill, không chạy tác vụ đánh giá, không thay đổi kết quả thí nghiệm.

## 1. Kết quả kiểm thử

Trong container Linux, bốn bộ test `test_01_provided.py`, `test_02_agent.py`, `test_03_runner.py`, `test_04_curator.py` đạt **29 passed in 8.19s**, mã thoát 0. Kết quả xác nhận các hành vi được bộ test bao phủ; không chứng minh mọi trường hợp biên đều đúng.

Kiểm tra bổ sung bằng mô hình giả xác nhận hai tên skill và chỉ dẫn `As your FIRST action` xuất hiện trong system prompt. Do đó chưa có bằng chứng lỗi nạp skill trong `build_agent`; `skills_read=0` ở các lần chạy thật phản ánh không có lệnh đọc nội dung skill trong vết luồng chính.

## 2. Phân biệt lỗi và trạng thái chưa thực hiện

| Hiện tượng | Bằng chứng và phân loại | Hướng xử lý |
|---|---|---|
| `tests_not_modified` thất bại ở code | Tái hiện trên bản sao workspace chưa có thao tác tác tử. Git báo `i/lf w/crlf`; hash sau chuẩn hóa xuống dòng khớp hash kỳ vọng. Đây là sai lệch bản checkout. | Dùng bản làm việc Linux với các tệp được cung cấp giữ đúng byte LF trong Git HEAD. Giữ nguyên bản checkout và kết quả hiện có; kiểm tra hash trước chạy. Các lần đo mới ghi thư mục khác và công khai thay đổi môi trường. Không sửa checker, test hoặc điểm JSON. |
| Hash skill Windows khác Linux | Windows: `cf27e9cb4cd695ff0a7ccaefd1d382493d13f58a85b234b99f95b490d578d96d`; Linux: `5a039da97ce7b0bdfaaf4000535ada94fe1db0884791e4d3bcdf68755de75b0b`. Tên đường dẫn tương đối dùng dấu phân cách khác nhau. | Chạy runner, curator và `verify_freeze.py` cùng môi trường Linux. Không sửa các hàm hash được cung cấp hoặc hash trong bản ghi. |
| Container thiếu Git | `shutil.which('git')` trả `None`. `verify_freeze.py` gọi Git qua subprocess. | Chuẩn bị môi trường Linux có Git trước Phần 4; có thể dùng image dẫn xuất bổ sung Git và lưu phiên bản. Sau đó kiểm tra tag, commit và chạy công cụ đóng băng tại cùng repo. |
| Skill được nạp nhưng không được đọc | Mô hình giả thấy cả hai skill và chỉ dẫn đọc trước; ba lần chạy thật có `skills_read=0`. | Giữ kết quả âm. Có thể chạy lại curator trong hạn mức repo nếu chất lượng/description không đạt; đánh giá và ghi lý do, không sửa tay skill. Hiện không có cơ sở khẳng định lỗi harness. Nếu thử thay đổi cơ chế đọc bắt buộc, phải là thí nghiệm mở rộng riêng vì prompt chính được bảo vệ. |
| Giao việc thiếu hoặc sai đặc tả | Data đổi khóa khử trùng; logs thiếu schema trong lời giao việc; code không có kiểm chứng của tác tử chính. | Trong thí nghiệm mở rộng, cải thiện description/system_prompt ở hàm subagent được phép sửa: yêu cầu xác nhận dữ kiện, đọc đặc tả gốc và báo cáo lệnh kiểm chứng. Giữ nguyên kết quả ban đầu, ghi rõ phiên bản và chạy riêng. Không ép sửa các hằng số prompt chung. |
| Đường dẫn shell, import và thiếu thư viện | Vết có `/workspace/...` không tồn tại, thiếu `inventory`, `pytz`, `dateutil`. | Shell dùng `workspace/...`; tác vụ code chạy từ thư mục workspace, ví dụ `cd workspace && python -m pytest tests`, hoặc `PYTHONPATH=workspace python -m pytest workspace/tests`. Tác vụ data ưu tiên thư viện chuẩn; nếu thêm dependency, ghi môi trường và chi phí. Không đưa lời nhắc mới vào prompt chung được bảo vệ. |
| Logs thiếu sự kiện hoặc sai UTC/traceback | Check count, UTC, exception và repeat count không đạt; tác tử viết JSON trực tiếp, không kiểm chứng bằng script. | Đề xuất quy trình đọc hết dữ liệu, phân nhóm sự kiện nhiều dòng, chuyển UTC bằng thư viện, tính `1 + sum(N)` rồi kiểm tra tổng và schema. Chỉ đưa vào skill qua curator hoặc thiết kế thí nghiệm mở rộng; không tự sửa đáp án workspace hoặc skill. |
| Chưa có tag `freeze` và kết quả đánh giá | Phần 4 chưa được cấp phép/thực hiện. | Đây là trạng thái đúng thứ tự, không phải lỗi. Viết và commit H1–H3 trước freeze; giữ skill từ thời điểm tag và chạy lại chính thức sau đó. |

## 3. Thứ tự đề xuất

1. Chuẩn bị môi trường Linux có Git và dữ liệu gốc LF, xác nhận hash trước khi chạy. Đây là ưu tiên tái lập trước Phần 4.
2. Giữ toàn bộ kết quả cũ và bản sao Phần 3.4; không sửa điểm. Nếu chuẩn hóa môi trường để đo lại, dùng thư mục kết quả mới, báo cáo lý do và cấu hình, xác định nhất quán bộ kết quả được so sánh.
3. Giữ nguyên skill hiện tại nếu tiếp tục thí nghiệm chính; kết quả không đọc skill là phát hiện hợp lệ. Các cải tiến subagent hoặc cơ chế đọc thuộc thí nghiệm riêng, không trộn với số liệu hiện có.
4. Sau khi người thực hiện duyệt bước tiếp theo, tiến hành giả thuyết và đóng băng theo GUIDE. Kiểm tra đóng băng phải chạy trong Linux có Git, cùng cách băm của runner.

## 4. Lệnh kiểm thử đã chạy

```bash
python -m pytest tests/test_01_provided.py tests/test_02_agent.py tests/test_03_runner.py tests/test_04_curator.py -ra
```

Lệnh chạy trong image `lab-deepagents`, repo gắn chỉ đọc. Các phép kiểm tra bổ sung dùng sandbox tạm và `ScriptedChatModel`; không tiêu thụ token API.
