# Script build tự động cho IUH Schedule Widget
Write-Host "🔨 Bắt đầu build..." -ForegroundColor Cyan

# Build với PyInstaller
& "D:\Schedule\.venv\Scripts\python.exe" -m PyInstaller --clean IUH_Schedule_Widget.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Build thành công!" -ForegroundColor Green
    
    # Copy file dữ liệu sang dist
    Write-Host "📋 Copy file dữ liệu..." -ForegroundColor Yellow
    Copy-Item "schedule_data.json" "dist\" -Force -ErrorAction SilentlyContinue
    
    # Liệt kê các file trong dist
    Write-Host "`n📁 Nội dung thư mục dist:" -ForegroundColor Cyan
    Get-ChildItem "dist\" | Format-Table Name, Length, LastWriteTime
    
    Write-Host "`n✨ Hoàn tất! Chạy app tại: dist\IUH_Schedule_Widget.exe" -ForegroundColor Green
} else {
    Write-Host "`n❌ Build thất bại!" -ForegroundColor Red
}
