from lib.irc import IrcClient


async def test_ircs_welcome(stack_factory):
    s = stack_factory()
    port = s.port("obbyircd", 6697)
    async with IrcClient("127.0.0.1", port, nick="installer") as c:
        await c.register()
        welcome = await c.expect(lambda l: " 001 " in l, timeout=30)
        assert "installer" in welcome


async def test_isupport_advertised(stack_factory):
    s = stack_factory()
    port = s.port("obbyircd", 6697)
    async with IrcClient("127.0.0.1", port, nick="isup") as c:
        await c.register()
        await c.expect(lambda l: "NETWORK=ObbyE2E" in l, timeout=30)
