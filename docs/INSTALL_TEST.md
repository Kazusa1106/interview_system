# 🔧 安装和测试指南

## 📦 步骤1: 安装依赖

```powershell
# 在项目目录下运行
pip install -r requirements.txt

# 如果需要升级gradio
pip install --upgrade gradio

# 验证安装
pip list | findstr "gradio plotly openai"
```

**预期输出**:
```
gradio              4.40.0 或更高
plotly              5.14.0 或更高
openai              1.20.0 或更高
```

## 🧪 步骤2: 运行功能测试

```powershell
# 运行完整测试套件
python test_features.py
```

**预期结果**: 所有6项测试应该通过：
- ✅ 数据库模块
- ✅ 可视化模块
- ✅ 会话管理器
- ✅ 管理后台
- ✅ Web界面
- ✅ 集成测试

## 🚀 步骤3: 启动系统

### 方式A: 一步启动（推荐用于测试）

```powershell
# 启动访谈界面
python main.py
# 选择 2 (Web模式)
```

### 方式B: 分别启动（推荐用于生产）

**终端1 - 访谈服务**:
```powershell
python main.py
# 选择 2
```

**终端2 - 管理后台**:
```powershell
python admin_server.py
```

## 🔍 步骤4: 验证功能

### 4.1 访谈功能测试

1. 浏览器打开: `http://localhost:7860`
2. 应该看到：
   - ✅ 渐变色紫色标题
   - ✅ 欢迎消息
   - ✅ 第一个问题
   - ✅ 侧边栏使用指南
3. 输入一个简单回答，点击发送
4. 观察是否有AI追问或进入下一题

### 4.2 数据持久化测试

1. 完成一次完整访谈（回答6个问题）
2. 按 `Ctrl+C` 停止服务
3. 检查是否生成了数据库文件：
   ```powershell
   dir interview_data.db
   ```
4. 重新启动服务：
   ```powershell
   python main.py
   # 选择 3 (管理后台)
   ```
5. 在管理后台中应该能看到刚才的访谈记录

### 4.3 管理后台测试

1. 浏览器打开: `http://localhost:7861`
2. 测试功能：

**概览标签**:
- 刷新概览 → 应显示统计数字
- 生成统计图表 → 应显示可视化图表
- 导出HTML报告 → 应显示成功消息和文件路径

**会话列表标签**:
- 刷新列表 → 应显示所有访谈
- 复制一个会话ID
- 粘贴到输入框，点击"查看详情"
- 应显示完整的对话记录

**数据管理标签**:
- 点击"导出所有会话"
- 应显示成功消息和导出文件列表

## ⚠️ 常见问题解决

### 问题1: SSL超时错误

**错误信息**: `socket.timeout: _ssl.c:1112: The handshake operation timed out`

**原因**: Gradio尝试连接外部服务器发送匿名统计，网络超时

**解决**: 这个错误不影响功能，可以忽略。或者设置环境变量：
```powershell
$env:GRADIO_ANALYTICS_ENABLED="False"
python main.py
```

### 问题2: 依赖安装失败

**错误信息**: `ERROR: No matching distribution found for python`

**原因**: requirements.txt包含了不可安装的python版本声明

**解决**: 已修复！重新运行：
```powershell
pip install -r requirements.txt
```

### 问题3: plotly未安装

**错误信息**: 管理后台图表显示警告

**解决**:
```powershell
pip install plotly
```

### 问题4: 数据库锁定

**错误信息**: `database is locked`

**原因**: 多个进程同时访问数据库

**解决**:
- 确保同时只运行一个访谈服务和一个管理后台
- 或者重启所有服务

### 问题5: 端口被占用

**错误信息**: `Address already in use`

**解决**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :7860
netstat -ano | findstr :7861

# 结束进程（替换PID）
taskkill /PID <进程ID> /F
```

## 📊 性能测试

### 测试并发访谈

1. 启动访谈服务
2. 在多个浏览器标签页中打开 `http://localhost:7860`
3. 同时在多个标签页中进行访谈
4. 验证：
   - ✅ 每个标签页独立会话
   - ✅ 数据正确保存
   - ✅ 管理后台能看到所有会话

### 测试数据量

1. 完成至少10次访谈
2. 打开管理后台
3. 生成统计图表
4. 验证：
   - ✅ 图表正确显示
   - ✅ 统计数据准确
   - ✅ HTML报告生成正常

## ✅ 测试检查清单

复制以下清单，测试时打勾：

```
基础功能：
[ ] 依赖安装成功
[ ] 功能测试全部通过
[ ] 访谈界面能正常打开
[ ] 管理后台能正常打开

访谈功能：
[ ] 能完成一次完整访谈
[ ] AI追问功能正常（如果配置了API）
[ ] 跳过按钮工作正常
[ ] 重新开始按钮工作正常

数据持久化：
[ ] 数据库文件自动创建
[ ] 访谈数据正确保存
[ ] 重启后数据不丢失
[ ] 能从数据库恢复会话

管理后台：
[ ] 概览统计显示正确
[ ] 会话列表显示正确
[ ] 会话详情查看正常
[ ] 统计图表生成正常
[ ] HTML报告导出正常
[ ] 批量导出功能正常

高级功能：
[ ] 多用户并发访谈正常
[ ] 数据可视化图表美观
[ ] 侧边栏指南显示正常
[ ] 进度条更新正确
```

## 🎉 测试完成

如果所有测试通过，恭喜！系统已经完全就绪，可以正式使用了。

**下一步**:
1. 配置API（如果需要AI追问）
2. 开始正式访谈
3. 定期查看管理后台统计
4. 定期备份 `interview_data.db`

**需要帮助**:
- 查看 README.md 了解完整功能
- 查看 QUICKSTART.md 了解快速使用
- 查看日志文件 logs/ 诊断问题
