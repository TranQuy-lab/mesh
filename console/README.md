# RescueSOS Console — app phía cứu hộ (Expo SDK 57)

App **cho đội cứu hộ / Ban chỉ huy** mang theo điện thoại: bản đồ SOS (MapLibre +
tile OpenStreetMap, không cần API key), la bàn chỉ đường tới SOS đang theo, danh
sách SOS ưu tiên, cấu hình server. Dựng bằng Expo + React Native, theo skill
`expo-ui`/`expo-design-system` (design tokens ở `src/constants/theme.ts`).

**Kiến trúc hai app:** app này CHỈ ĐỌC server (`GET /api/sos` 5 s/lượt) — việc
phát/nhảy SOS BLE thuộc app node native (`android-g0/`, vai trò nạn nhân/rơ).
Tách vai trò để app node giữ service nền bền + tiết kiệm pin (RN/Expo không làm
tốt BLE advertising nền), còn Console tối ưu trải nghiệm.

## Màn hình (Expo Router tabs)

| Tab | Nội dung |
|---|---|
| Bản đồ | MapLibre OSM, ghim SOS màu theo loại (đỏ=ngã, tím=chìm, cam=tay), BottomSheet chi tiết (@expo/ui), nút "Chỉ đường bằng la bàn" |
| La bàn | Kim chỉ tới SOS đang chọn (bearing − hướng máy), khoảng cách + hướng 8 cung |
| SOS | Danh sách hoạt động: trigger, hop, pin, GPS cấp, tuổi tin, số khung; chạm = đặt mục tiêu la bàn |
| Cấu hình | URL server (AsyncStorage), trạng thái kết nối, hướng dẫn adb reverse |

## Chạy

```bash
npm install
npx expo prebuild -p android      # sinh android/ (đã gitignore)
cd android && ./gradlew assembleDebug   # hoặc npx expo run:android
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb reverse tcp:8787 tcp:8787     # server SOS trên laptop → máy
# mở app: server mặc định http://127.0.0.1:8787 (adb reverse)
```

## Ghi chú trung thực

- Nền bản đồ OSM cần Internet; offline pack MapLibre là việc tiếp theo sau drill
  (khu vực chọn trước, tải trước khi mất sóng).
- La bàn dùng `expo-location.watchHeadingAsync` (la bàn máy); lệch từ tính gần
  kim loại — hiệu chuẩn hình số 8 khi nghi ngờ.
