"""
Rockstat calltracking structs
(c) Dmitry Rodin 2018
"""
import json
from prodict import Prodict
from typing import List, Any
from .helpers import ms, pairs
from band import logger

CTKEY = 'ctrack'


class StateUser(Prodict):
    phone: str
    act: int
    start: int
    sess: int


class State(Prodict):
    users: Prodict
    redis_pool: Any
    dyn_phones: List[int]
    fallback: int

    def free_phones(self) -> List[str]:
        return list(set(self.dyn_phones).difference([u.phone for u in self.users.values()]))

    async def set_user(self, uid, params):
        logger.info('setting user', uid=uid, u=params)
        self.users[uid] = StateUser.from_dict(params)
        await self.save_user(uid)

    async def touch(self, uid):
        if uid in self.users:
            diff = ms() - self.users[uid].act
            if diff > 2000:
                logger.debug('touching user', uid=uid, df=diff)
                self.users[uid].act = ms()
                await self.save_user(uid)

    async def save_user(self, uid):
        await self.hset(uid, self.users[uid])

    async def rm_user(self, uid):
        logger.info('removing user', uid=uid)
        self.users.pop(uid, None)
        await self.hdel(uid)

    async def hgetall(self):
        if self.redis_pool:
            with await self.redis_pool as conn:
                vals = await conn.execute('HGETALL', CTKEY)
                logger.info('vals', vals=vals)
                return {k.decode(): json.loads(v.decode()) for k, v in pairs(vals)}

    async def hset(self, uid, data):
        if self.redis_pool:
            with await self.redis_pool as conn:
                await conn.execute('HSET', CTKEY, uid.encode(), json.dumps(data).encode())

    async def hdel(self, uid):
        if self.redis_pool:
            with await self.redis_pool as conn:
                await conn.execute('HDEL', CTKEY, uid.encode())
