# 上位机开发 AI Agent 辅助系统

这是一个面向公司上位机开发场景的多 Agent 辅助系统 Demo，可用于审核展示。

## 功能

- 需求分析 Agent：把客户/公司需求拆分为功能模块
- 协议解析 Agent：解析帧头、字段、命令字和校验方式
- 代码生成 Agent：生成可运行的上位机 Tkinter 框架
- 日志诊断 Agent：分析校验失败、界面卡顿、串口占用、TCP 连接失败等问题
- 报告 Agent：生成项目分析报告

## 运行方式

```bash
python upper_computer_ai_agent_assistant.py
```

Python 版本建议：3.9 或以上。

本项目默认不需要第三方库。如果使用生成后的真实串口通信代码，可安装：

```bash
pip install pyserial
```


