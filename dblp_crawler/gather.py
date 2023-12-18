import asyncio


async def gather(*coros_or_futures):
    queue = asyncio.Queue()

    async def task(coro_or_future):
        result = await coro_or_future
        await queue.put(result)

    tasks = [task(c) for c in coros_or_futures]
    task_sum = asyncio.gather(*tasks)
    for _ in range(len(tasks)):
        yield await queue.get()
    await task_sum

if __name__ == "__main__":
    import random

    async def main():
        async def wait(n):
            await asyncio.sleep(n)
            return n
        tasks = [wait(n) for n in range(10)]
        random.shuffle(tasks)
        async for n in gather(*tasks):
            print(n)

    asyncio.run(main())
