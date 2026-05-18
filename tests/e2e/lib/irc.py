import asyncio
import ssl


class IrcClient:
    """Bare-bones async IRC over TLS for assertion-style tests."""

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __init__(self, host: str, port: int, nick: str = "tester"):
        self.host = host
        self.port = port
        self.nick = nick
        self.lines: list[str] = []

    async def __aenter__(self):
        ctx = ssl._create_unverified_context()
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port, ssl=ctx
        )
        return self

    async def __aexit__(self, *_):
        if hasattr(self, "writer"):
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except (ConnectionResetError, ssl.SSLError):
                pass

    async def send(self, line: str):
        self.writer.write(f"{line}\r\n".encode())
        await self.writer.drain()

    async def register(self):
        await self.send(f"NICK {self.nick}")
        await self.send(f"USER {self.nick} 0 * :{self.nick}")

    async def expect(self, predicate, timeout: float = 15) -> str:
        if isinstance(predicate, str):
            needle = predicate
            predicate = lambda l: needle in l
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remain = deadline - asyncio.get_event_loop().time()
            if remain <= 0:
                raise TimeoutError(f"never matched (last lines: {self.lines[-10:]})")
            try:
                raw = await asyncio.wait_for(self.reader.readline(), remain)
            except asyncio.TimeoutError:
                raise TimeoutError(f"never matched (last lines: {self.lines[-10:]})")
            if not raw:
                raise EOFError(f"connection closed (last lines: {self.lines[-10:]})")
            line = raw.decode(errors="replace").rstrip("\r\n")
            self.lines.append(line)
            if line.startswith("PING "):
                await self.send("PONG " + line.split(" ", 1)[1])
                continue
            if predicate(line):
                return line
