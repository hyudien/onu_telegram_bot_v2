"""ZTE OLT (C300/C320) telnet session"""

import re
import socket
import time
from contextlib import contextmanager

from app.config import OLT_HOST, OLT_PORT, OLT_USERNAME, OLT_PASSWORD

IAC, DONT, DO, WONT, WILL, SB, SE = 255, 254, 253, 252, 251, 250, 240
PROMPT_RE = re.compile(r"[\w\-./()]+[#>]\s*$")
MORE_RE = re.compile(r"--More--")


class OLTError(Exception):
    """Raised when the OLT cannot be reached or a command fails."""


class ZTESession:
    def __init__(self, host=OLT_HOST, port=OLT_PORT, username=OLT_USERNAME,
                 secret=OLT_PASSWORD, timeout=10):
        self.host, self.port = host, port
        self.username, self.secret = username, secret
        self.timeout = timeout
        self.sock = None

    # --- low level telnet ---
    def _recv(self) -> str:
        data = self.sock.recv(4096)
        if not data:
            raise OLTError("Koneksi ke OLT terputus")
        out = bytearray()
        i = 0
        while i < len(data):
            b = data[i]
            if b == IAC and i + 1 < len(data):
                cmd = data[i + 1]
                if cmd in (DO, DONT, WILL, WONT) and i + 2 < len(data):
                    reply = WONT if cmd in (DO, DONT) else DONT
                    self.sock.sendall(bytes([IAC, reply, data[i + 2]]))
                    i += 3
                    continue
                if cmd == SB:
                    end = data.find(bytes([IAC, SE]), i)
                    i = end + 2 if end != -1 else len(data)
                    continue
                i += 2
                continue
            out.append(b)
            i += 1
        return out.decode("utf-8", errors="ignore").replace("\r", "")

    def _read_until(self, pattern: re.Pattern, timeout=None) -> str:
        deadline = time.time() + (timeout or self.timeout)
        buf = ""
        while time.time() < deadline:
            try:
                chunk = self._recv()
            except socket.timeout:
                continue
            buf += chunk
            if MORE_RE.search(chunk):
                self.sock.sendall(b" ")
                buf = MORE_RE.sub("", buf)
                continue
            if pattern.search(buf):
                return buf
        raise OLTError("Timeout menunggu respon OLT")

    def _write(self, text: str) -> None:
        self.sock.sendall(text.encode("utf-8") + b"\r\n")

    # --- public API ---
    def open(self) -> None:
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.sock.settimeout(1)
        except OSError as e:
            raise OLTError(f"Tidak bisa terhubung ke OLT: {e}")
        self._read_until(re.compile(r"(?i)(username|login)\s*:\s*$"))
        self._write(self.username)
        self._read_until(re.compile(r"(?i)password\s*:\s*$"))
        self._write(self.secret)
        out = self._read_until(re.compile(r"(?i)(%?\s*(authentication failed|login invalid)|[#>]\s*$)"))
        if re.search(r"(?i)authentication failed|login invalid", out):
            raise OLTError("Login OLT gagal, periksa username/password")
        self.run("terminal length 0")

    def run(self, command: str, timeout=None) -> str:
        """Send a command and return its output (without echo/prompt)."""
        self._write(command)
        out = self._read_until(PROMPT_RE, timeout)
        lines = out.split("\n")
        if lines and command in lines[0]:
            lines = lines[1:]
        if lines and PROMPT_RE.search(lines[-1]):
            lines = lines[:-1]
        return "\n".join(lines).strip()

    def run_many(self, commands: list) -> str:
        """Run commands sequentially; raise OLTError on CLI errors."""
        result = []
        for cmd in commands:
            out = self.run(cmd)
            if re.search(r"%\s*(Error|Invalid|Unknown)|Invalid input", out, re.I):
                raise OLTError(f"Perintah gagal: {cmd}\n{out}")
            result.append(out)
        return "\n".join(result)

    def close(self) -> None:
        if self.sock:
            try:
                self._write("exit")
            except OSError:
                pass
            self.sock.close()
            self.sock = None


@contextmanager
def olt_session():
    session = ZTESession()
    try:
        session.open()
        yield session
    finally:
        session.close()


def onu_iface(pon: str, onu_id) -> str:
    """gpon-olt_1/1/1 + 5 -> gpon-onu_1/1/1:5"""
    return f"{pon.replace('gpon-olt_', 'gpon-onu_')}:{onu_id}"
