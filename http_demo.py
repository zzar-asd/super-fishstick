#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 协议演示代码（基于 Python 标准库，无需安装第三方依赖）

包含四个部分：
1. http_message  —— 手写 HTTP 报文的构造与解析（理解报文格式）
2. create_server —— 基于 http.server 的 REST 风格服务器（GET/POST/PUT/DELETE）
3. client_get/post —— 基于 urllib 的客户端请求
4. demo_protocol —— 用 socket 收发原始 TCP 字节，展示 HTTP 底层交互

运行方式：
    python3 http_demo.py            # 跑一遍完整演示
    python3 http_demo.py server     # 单独启动服务器（默认端口 8000）
"""

import json
import socket
import sys
import threading
import time
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


# ---------------------------------------------------------------------------
# 1. 手写 HTTP 报文的构造与解析（帮助理解协议本身）
# ---------------------------------------------------------------------------

def build_request(method: str, path: str, headers: dict | None = None,
                  body: bytes | str = b"") -> bytes:
    """构造一个 HTTP/1.1 请求报文（原始字节）。

    报文格式：
        请求行:   METHOD SP PATH SP HTTP/1.1 CRLF
        请求头:   Key: Value CRLF ...
        空行:     CRLF
        请求体:   （可选）
    """
    if isinstance(body, str):
        body = body.encode("utf-8")

    lines = [f"{method} {path} HTTP/1.1"]
    hdrs = {"Host": DEFAULT_HOST, "Connection": "close"}
    if body and "Content-Length" not in (headers or {}):
        hdrs["Content-Length"] = str(len(body))
    hdrs.update(headers or {})

    for k, v in hdrs.items():
        lines.append(f"{k}: {v}")

    head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
    return head + body


def parse_response(raw: bytes) -> dict:
    """解析一个 HTTP 响应报文（原始字节 -> 字典）。"""
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")

    # 状态行: HTTP/1.1 200 OK（reason 可能含空格，也可能缺失）
    status_parts = lines[0].split(" ", 2)
    version = status_parts[0]
    status_code = int(status_parts[1]) if len(status_parts) > 1 else 0
    reason = status_parts[2] if len(status_parts) > 2 else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    return {
        "version": version,
        "status": status_code,
        "reason": reason,
        "headers": headers,
        "body": body,
    }


# ---------------------------------------------------------------------------
# 2. REST 风格 HTTP 服务器（标准库 http.server）
# ---------------------------------------------------------------------------

# 内存"数据库"，用于演示增删改查
_DB: dict[str, dict] = {"1": {"id": "1", "name": "Alice"}}


class RestHandler(BaseHTTPRequestHandler):
    """简单的 JSON REST API：
        GET    /            -> 首页
        GET    /items       -> 列出所有资源
        GET    /items/<id>  -> 获取单个资源
        POST   /items       -> 创建资源
        PUT    /items/<id>  -> 更新资源
        DELETE /items/<id>  -> 删除资源
    """

    server_version = "HttpDemoPy/1.0"
    protocol_version = "HTTP/1.1"   # 使用 HTTP/1.1（配合 Content-Length 支持长连接）

    # ---- 工具方法 ----
    def _send_json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        # HEAD 请求按 RFC 9110 只返回报文头，不返回实体体
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except ValueError:                    # Content-Length 非法 -> 400
            return None
        raw = self.rfile.read(length) if length else b""
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    @staticmethod
    def _next_id() -> str:
        return str(max((int(k) for k in _DB), default=0) + 1)

    # ---- 路由分发 ----
    def _route(self, method: str):
        # 先剥离查询串（?a=1）与片段（#frag），避免 /items?x=1 被误判为 404
        path = urlparse(self.path).path.split("#", 1)[0]
        path = path.rstrip("/") or "/"
        parts = [p for p in path.split("/") if p]

        if parts == []:                       # GET / （HEAD 也走此分支，仅不返回实体体）
            if method in ("GET", "HEAD"):
                self._send_json({"message": "欢迎使用 HTTP 演示服务器",
                                 "endpoints": ["/", "/items", "/items/<id>"]})
            else:
                self._send_json({"error": "method not allowed"}, 405)
            return

        if parts[0] == "items":
            item_id = parts[1] if len(parts) > 1 else None

            # 非数字 id（如 /items/abc）直接视为不存在，返回 404
            if item_id is not None and not item_id.isdigit():
                self._send_json({"error": "not found"}, 404)
                return

            if method in ("GET", "HEAD"):
                if item_id is None:
                    self._send_json(list(_DB.values()))
                elif item_id in _DB:
                    self._send_json(_DB[item_id])
                else:
                    self._send_json({"error": "not found"}, 404)

            elif method in ("POST", "PUT") and \
                    (item_id is None if method == "POST" else item_id is not None):
                data = self._read_json_body()
                if data is None or not isinstance(data, dict):
                    self._send_json({"error": "invalid json"}, 400)
                    return
                if method == "POST":                       # 创建资源 -> 201
                    new_item = {"id": self._next_id(), **data}
                    _DB[new_item["id"]] = new_item
                    self._send_json(new_item, 201)
                else:                                      # PUT：更新资源
                    if item_id not in _DB:
                        self._send_json({"error": "not found"}, 404)
                        return
                    _DB[item_id].update(data)
                    self._send_json(_DB[item_id])

            elif method == "DELETE" and item_id:
                if item_id in _DB:
                    del _DB[item_id]
                    self._send_json({"deleted": item_id})
                else:
                    self._send_json({"error": "not found"}, 404)
            else:
                self._send_json({"error": "method not allowed"}, 405)
            return

        self._send_json({"error": "not found"}, 404)    # 未知路径

    # HTTP 方法入口
    def do_GET(self):    self._route("GET")
    def do_HEAD(self):   self._route("HEAD")   # HEAD 与 GET 路由相同，仅不返回实体体
    def do_POST(self):   self._route("POST")
    def do_PUT(self):    self._route("PUT")
    def do_DELETE(self): self._route("DELETE")

    # 未知路径的兜底错误处理：以 JSON 返回（默认实现会输出 HTML）
    def send_error(self, code, message=None, explain=None):
        if self.request_version != "HTTP/0.9":
            try:
                payload = json.dumps({"error": message or "error"},
                                     ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(payload)
                return
            except (BrokenPipeError, ConnectionResetError, OSError):
                return
        super().send_error(code, message, explain)

    # 静默默认日志（演示时输出更干净）
    def log_message(self, fmt, *args):
        pass


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, background=False):
    srv = ThreadingHTTPServer((host, port), RestHandler)
    print(f"[server] HTTP 服务已启动: http://{host}:{port}")
    if background:
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        return srv
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] 收到 Ctrl+C，正在关闭…")
    finally:
        srv.server_close()


# ---------------------------------------------------------------------------
# 3. HTTP 客户端（标准库 urllib）
# ---------------------------------------------------------------------------

def client_request(method: str, url: str, data: dict | None = None,
                   timeout: float = 5.0) -> tuple[int, dict]:
    """发送 HTTP 请求，返回 (状态码, 响应JSON)。"""
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urlrequest.Request(url, data=body, method=method,
                             headers={"Content-Type": "application/json"})
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:                      # 4xx / 5xx
        return e.code, json.loads(e.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# 4. Socket 层演示：观察 HTTP 的原始报文交互
# ---------------------------------------------------------------------------

def raw_http_exchange(host=DEFAULT_HOST, port=DEFAULT_PORT,
                      path="/items") -> dict:
    """用 TCP socket 手动发送请求报文并接收响应报文。"""
    raw_req = build_request("GET", path,
                            headers={"Accept": "application/json"})
    print("\n[socket] >>> 发送的原始请求报文:")
    print(raw_req.decode("latin-1").strip())

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(raw_req)
        chunks = []
        while True:
            piece = sock.recv(4096)
            if not piece:
                break
            chunks.append(piece)
    raw_resp = b"".join(chunks)

    print("[socket] <<< 收到的原始响应报文:")
    print(raw_resp.decode("latin-1").strip())

    parsed = parse_response(raw_resp)
    parsed["body"] = parsed["body"].decode("utf-8")
    return parsed


# ---------------------------------------------------------------------------
# 主程序：完整演示
# ---------------------------------------------------------------------------

def demo(host=DEFAULT_HOST, port=DEFAULT_PORT):
    base = f"http://{host}:{port}"
    srv = run_server(host, port, background=True)
    time.sleep(0.2)  # 等待服务器就绪
    try:
        print("=" * 60)
        print("① REST API 演示（urllib 客户端）")
        print("=" * 60)

        code, data = client_request("GET", base + "/")
        print(f"GET    /            -> {code} {data}")

        code, data = client_request("POST", base + "/items",
                                    {"name": "Bob", "role": "dev"})
        print(f"POST   /items       -> {code} {data}")
        new_id = data["id"]

        code, data = client_request("GET", base + f"/items/{new_id}")
        print(f"GET    /items/{new_id}      -> {code} {data}")

        code, data = client_request("PUT", base + f"/items/{new_id}",
                                    {"role": "lead"})
        print(f"PUT    /items/{new_id}      -> {code} {data}")

        code, data = client_request("GET", base + "/items")
        print(f"GET    /items       -> {code} {data}")

        code, data = client_request("DELETE", base + f"/items/{new_id}")
        print(f"DELETE /items/{new_id}      -> {code} {data}")

        code, data = client_request("GET", base + "/items/999")
        print(f"GET    /items/999   -> {code} {data}  (演示 404)")

        print()
        print("=" * 60)
        print("② Socket 层演示（原始 HTTP 报文）")
        print("=" * 60)
        parsed = raw_http_exchange(host, port)
        print(f"\n[socket] 解析结果: 版本={parsed['version']} "
              f"状态={parsed['status']} {parsed['reason']}")
        print(f"[socket] Content-Type = {parsed['headers'].get('content-type')}")
        print(f"[socket] Body = {parsed['body']}")
    finally:
        srv.shutdown()
        srv.server_close()
        print("\n[server] 已关闭，演示结束。")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # 单独前台运行服务器，方便浏览器访问
        port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
        run_server(port=port)
    else:
        demo()
