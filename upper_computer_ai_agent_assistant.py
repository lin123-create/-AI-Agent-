# -*- coding: utf-8 -*-
"""
上位机开发 AI Agent 辅助系统（单文件完整可运行版）
=====================================================

用途：
- 面向公司上位机开发场景，辅助完成需求拆解、协议解析、代码框架生成、日志诊断和项目报告整理。
- 可作为“Agent 或 AI 驱动构建具体成果”的审核演示项目。

运行：
    python upper_computer_ai_agent_assistant.py

说明：
- 本版本不依赖第三方库，使用 Python 标准库 + Tkinter。
- 内部使用规则引擎模拟多 Agent 协作，适合离线演示。
- 后续接入大模型 API 时，可替换 BaseAgent.ask_ai() 方法。
"""

from __future__ import annotations

import datetime as dt
import json
import re
import textwrap
import tkinter as tk
from dataclasses import asdict, dataclass, field
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Tuple


@dataclass
class RequirementModule:
    name: str
    description: str
    priority: str = "中"
    status: str = "待开发"


@dataclass
class ProtocolField:
    name: str
    length: int
    description: str
    example: str = ""


@dataclass
class ProtocolSpec:
    name: str = "未命名协议"
    transport: str = "串口 / TCP"
    frame_header: str = "AA 55"
    checksum: str = "SUM8"
    fields: List[ProtocolField] = field(default_factory=list)
    commands: Dict[str, str] = field(default_factory=dict)


@dataclass
class LogIssue:
    level: str
    symptom: str
    possible_reason: str
    suggestion: str


@dataclass
class ProjectContext:
    project_name: str = "工业设备上位机 AI Agent 辅助系统"
    requirement_text: str = ""
    protocol_text: str = ""
    log_text: str = ""
    modules: List[RequirementModule] = field(default_factory=list)
    protocol: ProtocolSpec = field(default_factory=ProtocolSpec)
    issues: List[LogIssue] = field(default_factory=list)
    generated_code: str = ""
    report_markdown: str = ""
    updated_at: str = field(default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def touch(self) -> None:
        self.updated_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class BaseAgent:
    name = "BaseAgent"
    role = "基础 Agent"

    def ask_ai(self, prompt: str) -> str:
        return "当前版本使用本地规则引擎，未接入外部大模型。"

    def run(self, ctx: ProjectContext) -> ProjectContext:
        raise NotImplementedError


class RequirementAgent(BaseAgent):
    name = "RequirementAgent"
    role = "需求分析 Agent"

    KEYWORDS = {
        "设备连接": ["串口", "COM", "TCP", "IP", "连接", "断开", "重连", "Modbus", "socket", "RS485"],
        "通信协议解析": ["协议", "帧头", "命令", "校验", "CRC", "SUM", "数据帧", "字节"],
        "实时数据显示": ["实时", "数据", "曲线", "波形", "温度", "压力", "速度", "电流", "电压", "采样"],
        "参数配置": ["参数", "配置", "阈值", "保存", "下发", "读取", "寄存器"],
        "报警管理": ["报警", "异常", "超限", "故障", "告警", "保护"],
        "数据存储": ["数据库", "CSV", "Excel", "保存", "历史", "记录", "导出"],
        "用户权限": ["登录", "权限", "管理员", "操作员", "账号"],
        "测试报告": ["测试", "报告", "记录", "结果", "验收", "归档"],
        "日志系统": ["日志", "log", "debug", "运行记录", "错误"],
        "自动化测试": ["自动测试", "脚本", "批量", "老化", "压力测试", "循环测试"],
        "界面交互": ["界面", "按钮", "表格", "UI", "显示", "窗口", "菜单"],
    }

    DESCRIPTIONS = {
        "设备连接": "负责串口、TCP/IP、RS485 或 Modbus 连接管理，包含连接、断开、状态检测和异常重连。",
        "通信协议解析": "负责数据帧封装、拆包、帧头识别、长度判断、命令字分发和校验处理。",
        "实时数据显示": "负责设备实时状态、关键参数、曲线数据和运行状态刷新。",
        "参数配置": "负责设备参数读取、修改、下发、校验和本地保存。",
        "报警管理": "负责异常状态判断、报警提示、报警记录和处理结果追踪。",
        "数据存储": "负责测试数据、运行数据和历史记录的本地存储与导出。",
        "用户权限": "负责登录认证、角色权限、操作记录和关键功能保护。",
        "测试报告": "负责自动整理测试步骤、测试结论、异常项和验收记录。",
        "日志系统": "负责通信日志、运行日志、异常日志的记录和检索。",
        "自动化测试": "负责批量测试、循环测试、压力测试和自动判断测试结果。",
        "界面交互": "负责主界面布局、按钮操作、表格展示和用户交互逻辑。",
    }

    DEFAULTS = [
        RequirementModule("设备连接", DESCRIPTIONS["设备连接"], "高"),
        RequirementModule("通信协议解析", DESCRIPTIONS["通信协议解析"], "高"),
        RequirementModule("实时数据显示", DESCRIPTIONS["实时数据显示"], "高"),
        RequirementModule("参数配置", DESCRIPTIONS["参数配置"], "中"),
        RequirementModule("日志系统", DESCRIPTIONS["日志系统"], "中"),
        RequirementModule("测试报告", DESCRIPTIONS["测试报告"], "中"),
    ]

    def run(self, ctx: ProjectContext) -> ProjectContext:
        text = ctx.requirement_text.strip()
        if not text:
            ctx.modules = list(self.DEFAULTS)
            ctx.touch()
            return ctx

        modules: List[RequirementModule] = []
        lower = text.lower()
        for module_name, keys in self.KEYWORDS.items():
            hit = sum(1 for k in keys if k.lower() in lower)
            if hit:
                priority = "高" if hit >= 2 or module_name in ("设备连接", "通信协议解析", "实时数据显示") else "中"
                modules.append(RequirementModule(module_name, self.DESCRIPTIONS[module_name], priority))

        if not modules:
            modules = list(self.DEFAULTS)

        must = ["设备连接", "通信协议解析", "日志系统"]
        existing = {m.name for m in modules}
        for name in reversed(must):
            if name not in existing:
                modules.insert(0, RequirementModule(name, self.DESCRIPTIONS[name], "高" if name != "日志系统" else "中"))

        ctx.modules = modules
        ctx.touch()
        return ctx


class ProtocolAgent(BaseAgent):
    name = "ProtocolAgent"
    role = "协议解析 Agent"

    def run(self, ctx: ProjectContext) -> ProjectContext:
        text = ctx.protocol_text.strip()
        spec = ProtocolSpec()
        if not text:
            spec.fields = self.default_fields(spec)
            spec.commands = self.default_commands()
            ctx.protocol = spec
            ctx.touch()
            return ctx

        name_match = re.search(r"(?:协议名称|name|protocol)[:：]\s*([^\n]+)", text, re.I)
        if name_match:
            spec.name = name_match.group(1).strip()

        if re.search(r"TCP|IP|socket|网口|以太网", text, re.I):
            spec.transport = "TCP/IP"
        elif re.search(r"Modbus", text, re.I):
            spec.transport = "Modbus"
        elif re.search(r"串口|RS485|RS232|COM|UART", text, re.I):
            spec.transport = "串口 / RS485"

        header_match = re.search(r"(?:帧头|header)[:：]?\s*((?:0x)?[0-9A-Fa-f]{2}(?:\s+(?:0x)?[0-9A-Fa-f]{2})*)", text)
        if header_match:
            spec.frame_header = header_match.group(1).replace("0x", "").replace("0X", "").upper()

        if re.search(r"CRC16", text, re.I):
            spec.checksum = "CRC16"
        elif re.search(r"CRC8", text, re.I):
            spec.checksum = "CRC8"
        elif re.search(r"XOR|异或", text, re.I):
            spec.checksum = "XOR"
        elif re.search(r"SUM|累加|和校验", text, re.I):
            spec.checksum = "SUM8"

        commands = {}
        for cmd, desc in re.findall(r"(?:0x)?([0-9A-Fa-f]{2})\s*[:：\-]\s*([^\n；;]+)", text):
            commands[f"0x{cmd.upper()}"] = desc.strip()
        spec.commands = commands or self.default_commands()

        fields: List[ProtocolField] = []
        patterns = [
            r"字段\s*[:：]?\s*([^,，\n]+)[,，]\s*长度\s*[:：]?\s*(\d+)[,，]\s*说明\s*[:：]?\s*([^\n]+)",
            r"(帧头|命令字|长度|数据长度|数据区|校验|CRC|地址|功能码)\s*[,，:：]?\s*(\d+)\s*(?:字节|byte|B)?\s*[,，:：]?\s*([^\n]*)",
        ]
        for pattern in patterns:
            for fname, flen, fdesc in re.findall(pattern, text, re.I):
                fname = fname.strip()
                if fname and all(f.name != fname for f in fields):
                    fields.append(ProtocolField(fname, int(flen), fdesc.strip() or "协议字段"))

        spec.fields = fields or self.default_fields(spec)
        ctx.protocol = spec
        ctx.touch()
        return ctx

    @staticmethod
    def default_commands() -> Dict[str, str]:
        return {
            "0x01": "读取设备状态",
            "0x02": "下发参数配置",
            "0x03": "启动测试流程",
            "0x04": "停止测试流程",
        }

    @staticmethod
    def default_fields(spec: ProtocolSpec) -> List[ProtocolField]:
        return [
            ProtocolField("帧头", 2, "固定帧头，用于识别数据帧起始位置", spec.frame_header),
            ProtocolField("命令字", 1, "表示当前数据帧功能类型", "01"),
            ProtocolField("数据长度", 1, "表示数据区长度", "04"),
            ProtocolField("数据区", 4, "实际业务数据，例如温度、电压、电流等", "00 19 03 E8"),
            ProtocolField("校验", 1, f"{spec.checksum} 校验", "B4"),
        ]


class LogAnalyzerAgent(BaseAgent):
    name = "LogAnalyzerAgent"
    role = "日志诊断 Agent"

    RULES: List[Tuple[str, str, str, str]] = [
        ("连接超时|timeout|timed out", "设备连接超时", "设备未上电、IP/端口错误、串口号错误、网络不通。", "检查设备电源、线缆、IP 地址、端口号和防火墙设置。"),
        ("校验失败|checksum|CRC", "协议校验失败", "校验算法不一致、数据帧丢字节、大小端或帧长度配置错误。", "核对校验范围、校验初值、字节序和帧尾处理。"),
        ("帧头错误|header", "帧头识别失败", "接收缓冲区未对齐、帧头配置错误或设备返回非协议数据。", "增加缓冲区滑动查找帧头逻辑，并确认帧头字节。"),
        ("拒绝连接|connection refused", "TCP 连接被拒绝", "目标端口未监听、设备服务未启动或端口号错误。", "确认设备 TCP Server 已启动，端口号与上位机配置一致。"),
        ("串口.*占用|access denied|PermissionError", "串口被占用", "串口已被其他软件打开，或权限不足。", "关闭串口助手等占用程序，重新插拔设备或以管理员权限运行。"),
        ("卡顿|无响应|界面卡死|freeze", "界面卡顿", "通信读取或数据处理放在 UI 主线程中执行。", "将通信接收、解析和耗时测试放入后台线程，通过队列刷新界面。"),
        ("乱码|decode|Unicode", "数据显示乱码", "编码格式不一致，或将二进制协议误按字符串解析。", "二进制协议使用 bytes/hex 显示，文本协议统一 UTF-8 或 GBK。"),
        ("丢包|漏包|数据不完整", "通信数据丢包", "读取频率不足、缓冲区过小、波特率过高或协议无帧边界处理。", "增加接收缓冲区、降低波特率、增加帧头帧长校验和重传机制。"),
    ]

    def run(self, ctx: ProjectContext) -> ProjectContext:
        text = ctx.log_text.strip()
        issues: List[LogIssue] = []
        for pattern, symptom, reason, suggestion in self.RULES:
            if text and re.search(pattern, text, re.I):
                issues.append(LogIssue("警告", symptom, reason, suggestion))
        if not issues:
            if text:
                issues.append(LogIssue("信息", "未匹配到典型错误", "日志中未发现常见通信或界面异常关键词。", "建议补充完整异常堆栈和原始收发数据后再次分析。"))
            else:
                issues.append(LogIssue("信息", "暂无日志", "未输入运行日志。", "可粘贴通信日志、异常报错或设备返回数据进行诊断。"))
        ctx.issues = issues
        ctx.touch()
        return ctx


class CodeGeneratorAgent(BaseAgent):
    name = "CodeGeneratorAgent"
    role = "代码生成 Agent"

    def run(self, ctx: ProjectContext) -> ProjectContext:
        ctx.generated_code = self.generate_upper_computer_code(ctx)
        ctx.touch()
        return ctx

    @staticmethod
    def generate_upper_computer_code(ctx: ProjectContext) -> str:
        protocol = ctx.protocol
        commands_repr = json.dumps(protocol.commands or ProtocolAgent.default_commands(), ensure_ascii=False, indent=4)
        header = protocol.frame_header or "AA 55"
        title = ctx.project_name.replace('"', '\\"')
        return f'''# -*- coding: utf-8 -*-
"""
{title} - Agent 自动生成的上位机框架
运行：python generated_upper_computer.py
"""

from __future__ import annotations

import csv
import datetime as dt
import queue
import socket
import threading
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk

try:
    import serial
    import serial.tools.list_ports
except Exception:
    serial = None

COMMANDS = {commands_repr}
FRAME_HEADER = bytes.fromhex("{header}")
CHECKSUM_MODE = "{protocol.checksum}"

@dataclass
class DeviceData:
    temperature: float = 0.0
    voltage: float = 0.0
    current: float = 0.0
    status: str = "离线"
    raw_hex: str = ""

class ProtocolCodec:
    @staticmethod
    def checksum(data: bytes) -> int:
        if CHECKSUM_MODE.upper() == "XOR":
            value = 0
            for b in data:
                value ^= b
            return value & 0xFF
        return sum(data) & 0xFF

    @classmethod
    def pack(cls, cmd: int, payload: bytes = b"") -> bytes:
        body = bytes([cmd & 0xFF, len(payload) & 0xFF]) + payload
        return FRAME_HEADER + body + bytes([cls.checksum(FRAME_HEADER + body)])

    @classmethod
    def parse(cls, frame: bytes) -> DeviceData:
        if len(frame) < len(FRAME_HEADER) + 3:
            raise ValueError("数据帧长度过短")
        if not frame.startswith(FRAME_HEADER):
            raise ValueError("帧头错误")
        if cls.checksum(frame[:-1]) != frame[-1]:
            raise ValueError("校验失败")
        idx = len(FRAME_HEADER)
        length = frame[idx + 1]
        payload = frame[idx + 2: idx + 2 + length]
        data = DeviceData(status="在线", raw_hex=frame.hex(" ").upper())
        if len(payload) >= 2:
            data.temperature = int.from_bytes(payload[0:2], "big", signed=True) / 10.0
        if len(payload) >= 4:
            data.voltage = int.from_bytes(payload[2:4], "big") / 100.0
        if len(payload) >= 6:
            data.current = int.from_bytes(payload[4:6], "big") / 1000.0
        return data

class SerialTransport:
    def __init__(self):
        self.ser = None
    def list_ports(self):
        if serial is None:
            return []
        return [p.device for p in serial.tools.list_ports.comports()]
    def open(self, port: str, baudrate: int):
        if serial is None:
            raise RuntimeError("未安装 pyserial，请执行 pip install pyserial")
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
    def close(self):
        if self.ser:
            self.ser.close(); self.ser = None
    def write(self, data: bytes):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("串口未打开")
        self.ser.write(data)
    def read_available(self) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b""
        return self.ser.read(self.ser.in_waiting) if self.ser.in_waiting else b""

class TcpTransport:
    def __init__(self):
        self.sock = None
    def open(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=3)
        self.sock.settimeout(0.1)
    def close(self):
        if self.sock:
            self.sock.close(); self.sock = None
    def write(self, data: bytes):
        if not self.sock:
            raise RuntimeError("TCP 未连接")
        self.sock.sendall(data)
    def read_available(self) -> bytes:
        if not self.sock:
            return b""
        try:
            return self.sock.recv(4096)
        except socket.timeout:
            return b""

class UpperComputerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("{title}")
        self.geometry("1100x720")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transport_type = tk.StringVar(value="串口")
        self.port_var = tk.StringVar(value="COM1")
        self.baud_var = tk.StringVar(value="115200")
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.tcp_port_var = tk.StringVar(value="502")
        self.status_var = tk.StringVar(value="未连接")
        self.transport = None
        self.running = False
        self.rx_queue = queue.Queue()
        self.records = []
        self.create_widgets()
        self.after(200, self.poll_rx_queue)

    def create_widgets(self):
        root = ttk.Frame(self, padding=10); root.pack(fill=tk.BOTH, expand=True)
        left = ttk.LabelFrame(root, text="连接与命令", padding=10); left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        ttk.Label(left, text="通信方式").pack(anchor="w")
        ttk.Combobox(left, textvariable=self.transport_type, values=["串口", "TCP"], state="readonly", width=18).pack(anchor="w", pady=4)
        ttk.Label(left, text="串口号").pack(anchor="w")
        ttk.Entry(left, textvariable=self.port_var, width=18).pack(anchor="w", pady=4)
        ttk.Label(left, text="波特率").pack(anchor="w")
        ttk.Entry(left, textvariable=self.baud_var, width=18).pack(anchor="w", pady=4)
        ttk.Label(left, text="TCP 地址").pack(anchor="w")
        ttk.Entry(left, textvariable=self.host_var, width=18).pack(anchor="w", pady=4)
        ttk.Label(left, text="TCP 端口").pack(anchor="w")
        ttk.Entry(left, textvariable=self.tcp_port_var, width=18).pack(anchor="w", pady=4)
        ttk.Button(left, text="连接设备", command=self.connect_device).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="断开连接", command=self.disconnect_device).pack(fill=tk.X, pady=3)
        ttk.Label(left, textvariable=self.status_var, foreground="blue").pack(anchor="w", pady=8)
        ttk.Separator(left).pack(fill=tk.X, pady=8)
        for cmd_hex, desc in COMMANDS.items():
            try: cmd = int(cmd_hex, 16)
            except Exception: cmd = 1
            ttk.Button(left, text=f"{{cmd_hex}} {{desc}}", command=lambda c=cmd: self.send_command(c)).pack(fill=tk.X, pady=2)
        ttk.Button(left, text="模拟接收数据", command=self.simulate_receive).pack(fill=tk.X, pady=8)
        ttk.Button(left, text="导出 CSV", command=self.export_csv).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="导出测试报告", command=self.export_report).pack(fill=tk.X, pady=3)

        right = ttk.Frame(root); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        top = ttk.LabelFrame(right, text="实时数据", padding=10); top.pack(fill=tk.X)
        self.data_vars = {{}}
        for i, key in enumerate(["temperature", "voltage", "current", "status", "raw_hex"]):
            ttk.Label(top, text=key).grid(row=i//2, column=(i%2)*2, sticky="w", padx=6, pady=5)
            var = tk.StringVar(value="-"); self.data_vars[key] = var
            ttk.Label(top, textvariable=var, width=42).grid(row=i//2, column=(i%2)*2+1, sticky="w", padx=6, pady=5)
        mid = ttk.LabelFrame(right, text="运行日志", padding=10); mid.pack(fill=tk.BOTH, expand=True, pady=8)
        self.log_text = tk.Text(mid, height=16); self.log_text.pack(fill=tk.BOTH, expand=True)
        bottom = ttk.LabelFrame(right, text="数据记录", padding=10); bottom.pack(fill=tk.BOTH, expand=True)
        columns = ("time", "temperature", "voltage", "current", "status", "raw")
        self.tree = ttk.Treeview(bottom, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col); self.tree.column(col, width=120 if col != "raw" else 260)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def connect_device(self):
        try:
            if self.transport_type.get() == "串口":
                self.transport = SerialTransport(); self.transport.open(self.port_var.get(), int(self.baud_var.get()))
            else:
                self.transport = TcpTransport(); self.transport.open(self.host_var.get(), int(self.tcp_port_var.get()))
            self.running = True
            threading.Thread(target=self.read_loop, daemon=True).start()
            self.status_var.set("已连接"); self.log("设备连接成功")
        except Exception as exc:
            self.status_var.set("连接失败"); self.log(f"连接失败：{{exc}}"); messagebox.showerror("连接失败", str(exc))

    def disconnect_device(self):
        self.running = False
        try:
            if self.transport: self.transport.close()
        except Exception: pass
        self.status_var.set("已断开"); self.log("设备已断开")

    def read_loop(self):
        while self.running:
            try:
                data = self.transport.read_available() if self.transport else b""
                if data: self.rx_queue.put(data)
            except Exception as exc:
                self.rx_queue.put(exc); break

    def poll_rx_queue(self):
        while not self.rx_queue.empty():
            item = self.rx_queue.get()
            if isinstance(item, Exception): self.log(f"接收异常：{{item}}")
            else: self.handle_frame(item)
        self.after(200, self.poll_rx_queue)

    def send_command(self, cmd: int):
        try:
            frame = ProtocolCodec.pack(cmd)
            if self.transport: self.transport.write(frame)
            self.log("发送：" + frame.hex(" ").upper())
        except Exception as exc:
            self.log(f"发送失败：{{exc}}")

    def simulate_receive(self):
        payload = int(256).to_bytes(2, "big", signed=True) + int(1200).to_bytes(2, "big") + int(320).to_bytes(2, "big")
        self.handle_frame(ProtocolCodec.pack(0x01, payload))

    def handle_frame(self, frame: bytes):
        try:
            data = ProtocolCodec.parse(frame)
            self.data_vars["temperature"].set(f"{{data.temperature:.1f}} ℃")
            self.data_vars["voltage"].set(f"{{data.voltage:.2f}} V")
            self.data_vars["current"].set(f"{{data.current:.3f}} A")
            self.data_vars["status"].set(data.status)
            self.data_vars["raw_hex"].set(data.raw_hex)
            row = {{"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "temperature": data.temperature, "voltage": data.voltage, "current": data.current, "status": data.status, "raw": data.raw_hex}}
            self.records.append(row)
            self.tree.insert("", tk.END, values=(row["time"], row["temperature"], row["voltage"], row["current"], row["status"], row["raw"]))
            self.log("接收解析成功：" + data.raw_hex)
        except Exception as exc:
            self.log("协议解析失败：" + str(exc) + "，原始数据=" + frame.hex(" ").upper())

    def log(self, message: str):
        self.log_text.insert(tk.END, f"[{{dt.datetime.now().strftime('%H:%M:%S')}}] {{message}}\n")
        self.log_text.see(tk.END)

    def export_csv(self):
        if not self.records:
            messagebox.showinfo("提示", "暂无数据记录"); return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
        if not path: return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["time", "temperature", "voltage", "current", "status", "raw"])
            writer.writeheader(); writer.writerows(self.records)
        self.log(f"CSV 已导出：{{path}}")

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown 文件", "*.md")])
        if not path: return
        content = f"""# 上位机测试报告\n\n生成时间：{{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}\n\n## 测试概述\n验证通信连接、协议解析、实时数据显示、日志记录和数据导出功能。\n\n## 测试结果\n- 数据记录数量：{{len(self.records)}}\n- 最新状态：{{self.records[-1]['status'] if self.records else '-'}}\n\n## 结论\n若通信稳定、解析正确、导出完整，则基础功能测试通过。\n"""
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        self.log(f"测试报告已导出：{{path}}")

    def on_close(self):
        self.disconnect_device(); self.destroy()

if __name__ == "__main__":
    UpperComputerApp().mainloop()
'''


class ReportAgent(BaseAgent):
    name = "ReportAgent"
    role = "报告生成 Agent"

    def run(self, ctx: ProjectContext) -> ProjectContext:
        ctx.report_markdown = self.build_report(ctx)
        ctx.touch()
        return ctx

    @staticmethod
    def build_report(ctx: ProjectContext) -> str:
        module_lines = "\n".join(
            f"| {i+1} | {m.name} | {m.description} | {m.priority} | {m.status} |"
            for i, m in enumerate(ctx.modules)
        ) or "| - | - | - | - | - |"
        field_lines = "\n".join(
            f"| {f.name} | {f.length} | {f.description} | {f.example} |"
            for f in ctx.protocol.fields
        ) or "| - | - | - | - |"
        command_lines = "\n".join(f"| {k} | {v} |" for k, v in ctx.protocol.commands.items()) or "| - | - |"
        issue_lines = "\n".join(
            f"| {i.level} | {i.symptom} | {i.possible_reason} | {i.suggestion} |"
            for i in ctx.issues
        ) or "| - | - | - | - |"
        return f"""# {ctx.project_name} 项目分析报告

生成时间：{ctx.updated_at}

## 1. 项目目标

本项目面向公司工业设备上位机开发场景，使用多个 AI Agent 对需求分析、通信协议解析、代码框架生成、日志诊断和测试报告整理进行辅助，减少重复开发和人工排查时间，提升项目交付效率与文档规范性。

## 2. 核心痛点

1. 上位机需求经常来自客户口头描述或零散文档，功能边界不清晰。  
2. 串口、TCP/IP、Modbus 等通信协议容易出现帧头、长度、校验、字节序错误。  
3. 界面、日志、数据导出、测试报告等功能重复开发较多。  
4. 调试日志分散，问题定位依赖个人经验，新人接手成本较高。  
5. 项目交付时需要同步整理测试记录和验收文档，人工整理效率较低。  

## 3. 多 Agent 工作流

- 需求分析 Agent：将客户需求拆分为可开发模块。  
- 协议解析 Agent：根据协议说明抽取帧结构、命令字和校验方式。  
- 代码生成 Agent：生成上位机基础代码框架，包括通信、解析、界面、日志和导出功能。  
- 日志分析 Agent：根据异常日志识别常见通信和界面问题。  
- 报告 Agent：汇总模块、协议、问题和测试结论，生成公司归档文档。  

## 4. 功能模块拆解

| 序号 | 模块 | 说明 | 优先级 | 状态 |
|---|---|---|---|---|
{module_lines}

## 5. 通信协议概要

- 协议名称：{ctx.protocol.name}
- 传输方式：{ctx.protocol.transport}
- 帧头：{ctx.protocol.frame_header}
- 校验方式：{ctx.protocol.checksum}

### 5.1 字段结构

| 字段 | 长度/字节 | 说明 | 示例 |
|---|---:|---|---|
{field_lines}

### 5.2 命令字

| 命令字 | 功能说明 |
|---|---|
{command_lines}

## 6. 日志诊断结果

| 级别 | 现象 | 可能原因 | 建议处理 |
|---|---|---|---|
{issue_lines}

## 7. 交付价值

该系统可在公司内部上位机项目中复用，适用于设备调试、产线测试、自动化检测和售后问题定位等场景。通过 Agent 工作流，可以将需求拆解、协议梳理、代码框架生成、日志分析和报告整理统一到一个工具中，减少重复劳动，提高交付效率。

## 8. 后续扩展方向

1. 接入真实大模型 API，实现更灵活的需求理解和代码生成。  
2. 增加 Modbus RTU/TCP、CAN、MQTT 等协议模板。  
3. 增加 C# WinForms/WPF、Qt、PySide6 等多语言代码模板。  
4. 增加设备自动化测试脚本执行能力。  
5. 增加公司内部项目知识库检索功能。  
"""


class AgentOrchestrator:
    def __init__(self):
        self.requirement_agent = RequirementAgent()
        self.protocol_agent = ProtocolAgent()
        self.code_agent = CodeGeneratorAgent()
        self.log_agent = LogAnalyzerAgent()
        self.report_agent = ReportAgent()

    def run_all(self, ctx: ProjectContext) -> ProjectContext:
        for agent in [self.requirement_agent, self.protocol_agent, self.code_agent, self.log_agent, self.report_agent]:
            ctx = agent.run(ctx)
        return ctx


class AgentAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("上位机开发 AI Agent 辅助系统")
        self.geometry("1260x820")
        self.minsize(1100, 720)
        self.ctx = ProjectContext()
        self.orchestrator = AgentOrchestrator()
        self.project_name_var = tk.StringVar(value=self.ctx.project_name)
        self.status_var = tk.StringVar(value="就绪")
        self.create_widgets()
        self.load_default_example()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        top = ttk.Frame(self, padding=(10, 8))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="项目名称：").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.project_name_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(top, text="运行全部 Agent", command=self.run_all_agents).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="保存项目 JSON", command=self.save_project).grid(row=0, column=3, padx=4)
        ttk.Button(top, text="打开项目 JSON", command=self.open_project).grid(row=0, column=4, padx=4)

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        left = ttk.Frame(paned); right = ttk.Frame(paned)
        paned.add(left, weight=1); paned.add(right, weight=1)

        self.input_tabs = ttk.Notebook(left); self.input_tabs.pack(fill=tk.BOTH, expand=True)
        self.requirement_text = self.make_text_tab(self.input_tabs, "需求输入")
        self.protocol_text = self.make_text_tab(self.input_tabs, "协议输入")
        self.log_text = self.make_text_tab(self.input_tabs, "日志输入")

        buttons = ttk.Frame(left); buttons.pack(fill=tk.X, pady=6)
        ttk.Button(buttons, text="需求分析", command=self.run_requirement).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons, text="协议解析", command=self.run_protocol).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons, text="日志诊断", command=self.run_log).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons, text="载入示例", command=self.load_default_example).pack(side=tk.RIGHT, padx=3)

        self.output_tabs = ttk.Notebook(right); self.output_tabs.pack(fill=tk.BOTH, expand=True)
        self.modules_frame = ttk.Frame(self.output_tabs, padding=8)
        self.protocol_frame = ttk.Frame(self.output_tabs, padding=8)
        self.issues_frame = ttk.Frame(self.output_tabs, padding=8)
        self.output_tabs.add(self.modules_frame, text="模块拆解")
        self.output_tabs.add(self.protocol_frame, text="协议结果")
        self.output_tabs.add(self.issues_frame, text="诊断结果")
        self.code_text = self.make_text_tab(self.output_tabs, "生成代码")
        self.report_text = self.make_text_tab(self.output_tabs, "项目报告")
        self.create_modules_table()
        self.create_protocol_table()
        self.create_issues_table()

        rbuttons = ttk.Frame(right); rbuttons.pack(fill=tk.X, pady=6)
        ttk.Button(rbuttons, text="生成代码", command=self.run_code).pack(side=tk.LEFT, padx=3)
        ttk.Button(rbuttons, text="生成报告", command=self.run_report).pack(side=tk.LEFT, padx=3)
        ttk.Button(rbuttons, text="导出生成代码 .py", command=self.export_code).pack(side=tk.RIGHT, padx=3)
        ttk.Button(rbuttons, text="导出报告 .md", command=self.export_report).pack(side=tk.RIGHT, padx=3)

        bottom = ttk.Frame(self, padding=(10, 4)); bottom.grid(row=2, column=0, sticky="ew")
        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT)

    @staticmethod
    def make_text_tab(notebook: ttk.Notebook, title: str) -> tk.Text:
        frame = ttk.Frame(notebook, padding=6)
        text = tk.Text(frame, wrap=tk.WORD, undo=True)
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        notebook.add(frame, text=title)
        return text

    def create_modules_table(self):
        self.modules_tree = ttk.Treeview(self.modules_frame, columns=("name", "desc", "priority", "status"), show="headings")
        for col, title, width in [("name", "模块", 130), ("desc", "说明", 520), ("priority", "优先级", 80), ("status", "状态", 80)]:
            self.modules_tree.heading(col, text=title); self.modules_tree.column(col, width=width)
        self.modules_tree.pack(fill=tk.BOTH, expand=True)

    def create_protocol_table(self):
        self.protocol_summary_var = tk.StringVar(value="暂无协议结果")
        ttk.Label(self.protocol_frame, textvariable=self.protocol_summary_var).pack(anchor="w")
        self.protocol_tree = ttk.Treeview(self.protocol_frame, columns=("name", "length", "desc", "example"), show="headings")
        for col, title, width in [("name", "字段", 120), ("length", "长度", 70), ("desc", "说明", 430), ("example", "示例", 120)]:
            self.protocol_tree.heading(col, text=title); self.protocol_tree.column(col, width=width)
        self.protocol_tree.pack(fill=tk.BOTH, expand=True, pady=8)
        self.command_text = tk.Text(self.protocol_frame, height=8)
        self.command_text.pack(fill=tk.BOTH, expand=True)

    def create_issues_table(self):
        self.issues_tree = ttk.Treeview(self.issues_frame, columns=("level", "symptom", "reason", "suggestion"), show="headings")
        for col, title, width in [("level", "级别", 70), ("symptom", "现象", 150), ("reason", "可能原因", 320), ("suggestion", "建议处理", 360)]:
            self.issues_tree.heading(col, text=title); self.issues_tree.column(col, width=width)
        self.issues_tree.pack(fill=tk.BOTH, expand=True)

    def load_default_example(self):
        self.requirement_text.delete("1.0", tk.END)
        self.requirement_text.insert("1.0", textwrap.dedent("""
            公司需要开发一套工业检测设备上位机软件，用于产线调试和售后检测。
            软件需要支持串口和 TCP 连接设备，能够读取设备实时温度、电压、电流和运行状态。
            需要支持参数配置下发、阈值设置、测试启动/停止、异常报警提示。
            测试数据需要保存为 CSV，后续可以导出测试报告。
            软件需要记录通信日志和异常日志，方便售后工程师定位问题。
        """).strip())
        self.protocol_text.delete("1.0", tk.END)
        self.protocol_text.insert("1.0", textwrap.dedent("""
            协议名称：工业检测设备自定义协议
            传输方式：串口 RS485 或 TCP/IP
            帧头：AA 55
            校验方式：SUM8
            字段：帧头，长度：2，说明：固定帧头
            字段：命令字，长度：1，说明：功能码
            字段：数据长度，长度：1，说明：数据区字节数
            字段：数据区，长度：6，说明：温度、电压、电流
            字段：校验，长度：1，说明：对前面所有字节累加取低八位
            01：读取设备状态
            02：下发参数配置
            03：开始测试
            04：停止测试
        """).strip())
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert("1.0", textwrap.dedent("""
            10:21:08 打开 COM3 成功
            10:21:09 发送 AA 55 01 00 00
            10:21:09 接收 AA 55 01 06 01 00 04 B0 01 40 5C
            10:21:10 校验失败，接收=5C，计算=5B
            10:21:15 界面偶尔卡顿，无响应
        """).strip())
        self.status_var.set("已载入上位机项目示例")

    def update_context_from_inputs(self):
        self.ctx.project_name = self.project_name_var.get().strip() or self.ctx.project_name
        self.ctx.requirement_text = self.requirement_text.get("1.0", tk.END).strip()
        self.ctx.protocol_text = self.protocol_text.get("1.0", tk.END).strip()
        self.ctx.log_text = self.log_text.get("1.0", tk.END).strip()
        self.ctx.touch()

    def refresh_outputs(self):
        self.refresh_modules(); self.refresh_protocol(); self.refresh_issues()
        self.code_text.delete("1.0", tk.END); self.code_text.insert("1.0", self.ctx.generated_code)
        self.report_text.delete("1.0", tk.END); self.report_text.insert("1.0", self.ctx.report_markdown)

    def refresh_modules(self):
        for item in self.modules_tree.get_children(): self.modules_tree.delete(item)
        for m in self.ctx.modules: self.modules_tree.insert("", tk.END, values=(m.name, m.description, m.priority, m.status))

    def refresh_protocol(self):
        p = self.ctx.protocol
        self.protocol_summary_var.set(f"协议：{p.name} | 传输：{p.transport} | 帧头：{p.frame_header} | 校验：{p.checksum}")
        for item in self.protocol_tree.get_children(): self.protocol_tree.delete(item)
        for f in p.fields: self.protocol_tree.insert("", tk.END, values=(f.name, f.length, f.description, f.example))
        self.command_text.delete("1.0", tk.END)
        self.command_text.insert("1.0", "命令字：\n" + "\n".join(f"{k}：{v}" for k, v in p.commands.items()))

    def refresh_issues(self):
        for item in self.issues_tree.get_children(): self.issues_tree.delete(item)
        for i in self.ctx.issues: self.issues_tree.insert("", tk.END, values=(i.level, i.symptom, i.possible_reason, i.suggestion))

    def run_all_agents(self):
        self.update_context_from_inputs()
        self.ctx = self.orchestrator.run_all(self.ctx)
        self.refresh_outputs()
        self.status_var.set("已完成全部 Agent 流程")

    def run_requirement(self):
        self.update_context_from_inputs(); self.ctx = RequirementAgent().run(self.ctx); self.refresh_modules(); self.status_var.set("需求分析完成")

    def run_protocol(self):
        self.update_context_from_inputs(); self.ctx = ProtocolAgent().run(self.ctx); self.refresh_protocol(); self.status_var.set("协议解析完成")

    def run_log(self):
        self.update_context_from_inputs(); self.ctx = LogAnalyzerAgent().run(self.ctx); self.refresh_issues(); self.status_var.set("日志诊断完成")

    def run_code(self):
        self.update_context_from_inputs()
        if not self.ctx.modules: self.ctx = RequirementAgent().run(self.ctx)
        if not self.ctx.protocol.fields: self.ctx = ProtocolAgent().run(self.ctx)
        self.ctx = CodeGeneratorAgent().run(self.ctx)
        self.code_text.delete("1.0", tk.END); self.code_text.insert("1.0", self.ctx.generated_code)
        self.status_var.set("代码生成完成")

    def run_report(self):
        self.update_context_from_inputs()
        if not self.ctx.modules: self.ctx = RequirementAgent().run(self.ctx)
        if not self.ctx.protocol.fields: self.ctx = ProtocolAgent().run(self.ctx)
        if not self.ctx.issues: self.ctx = LogAnalyzerAgent().run(self.ctx)
        self.ctx = ReportAgent().run(self.ctx)
        self.report_text.delete("1.0", tk.END); self.report_text.insert("1.0", self.ctx.report_markdown)
        self.status_var.set("报告生成完成")

    def export_code(self):
        code = self.code_text.get("1.0", tk.END).strip()
        if not code:
            messagebox.showinfo("提示", "请先生成代码"); return
        path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python 文件", "*.py")], initialfile="generated_upper_computer.py")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: f.write(code)
        self.status_var.set(f"代码已导出：{path}")

    def export_report(self):
        report = self.report_text.get("1.0", tk.END).strip()
        if not report:
            messagebox.showinfo("提示", "请先生成报告"); return
        path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown 文件", "*.md")], initialfile="upper_computer_agent_report.md")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: f.write(report)
        self.status_var.set(f"报告已导出：{path}")

    def save_project(self):
        self.update_context_from_inputs()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON 文件", "*.json")], initialfile="upper_computer_agent_project.json")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: json.dump(asdict(self.ctx), f, ensure_ascii=False, indent=2)
        self.status_var.set(f"项目已保存：{path}")

    def open_project(self):
        path = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            self.ctx = self.context_from_dict(data)
            self.project_name_var.set(self.ctx.project_name)
            self.requirement_text.delete("1.0", tk.END); self.requirement_text.insert("1.0", self.ctx.requirement_text)
            self.protocol_text.delete("1.0", tk.END); self.protocol_text.insert("1.0", self.ctx.protocol_text)
            self.log_text.delete("1.0", tk.END); self.log_text.insert("1.0", self.ctx.log_text)
            self.refresh_outputs(); self.status_var.set(f"项目已打开：{path}")
        except Exception as exc:
            messagebox.showerror("打开失败", str(exc))

    @staticmethod
    def context_from_dict(data: dict) -> ProjectContext:
        modules = [RequirementModule(**m) for m in data.get("modules", [])]
        p_data = data.get("protocol", {}) or {}
        fields = [ProtocolField(**f) for f in p_data.get("fields", [])]
        protocol = ProtocolSpec(
            name=p_data.get("name", "未命名协议"),
            transport=p_data.get("transport", "串口 / TCP"),
            frame_header=p_data.get("frame_header", "AA 55"),
            checksum=p_data.get("checksum", "SUM8"),
            fields=fields,
            commands=p_data.get("commands", {}),
        )
        issues = [LogIssue(**i) for i in data.get("issues", [])]
        return ProjectContext(
            project_name=data.get("project_name", "工业设备上位机 AI Agent 辅助系统"),
            requirement_text=data.get("requirement_text", ""),
            protocol_text=data.get("protocol_text", ""),
            log_text=data.get("log_text", ""),
            modules=modules,
            protocol=protocol,
            issues=issues,
            generated_code=data.get("generated_code", ""),
            report_markdown=data.get("report_markdown", ""),
            updated_at=data.get("updated_at", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )


if __name__ == "__main__":
    AgentAssistantApp().mainloop()
