import asyncio

from integration.processor import replace_username


class FakeResult:
    def __init__(self, upserted_id):
        self.upserted_id = upserted_id


class FakeCollection:
    def __init__(self):
        self.docs = set()

    async def update_one(self, query, update, upsert=False):
        key = (query['source_channel_id'], query['source_message_id'])
        if key in self.docs:
            return FakeResult(None)
        self.docs.add(key)
        return FakeResult(key)


async def main():
    assert replace_username('Amavasya.Ep01.1080p.@oldusername.mkv', '@example') == 'Amavasya.Ep01.1080p.@example.mkv'
    assert replace_username('Anime_Name_S01E01_720p_@abc.mkv', '@example') == 'Anime_Name_S01E01_720p_@example.mkv'
    assert replace_username('NoUsername.mkv', '@example') == 'NoUsername.mkv'
    assert replace_username('x.@one.@two.mkv', '@new') == 'x.@new.@two.mkv'
    store = FakeCollection()
    first = await store.update_one({'source_channel_id': -1001, 'source_message_id': 7}, {}, upsert=True)
    second = await store.update_one({'source_channel_id': -1001, 'source_message_id': 7}, {}, upsert=True)
    assert first.upserted_id is not None
    assert second.upserted_id is None
    print('integration tests: PASS')


if __name__ == '__main__':
    asyncio.run(main())
