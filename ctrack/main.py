"""
Rockstat calltracking main
(c) Dmitry Rodin 2018
"""
import asyncio
from prodict import Prodict as pdict
from band import expose, worker, settings, logger, redis_factory, scheduler
from .structs import State
from .helpers import rand_item, ms
logger.info('p', p=settings.phones)
state = State(users=pdict(), **settings.phones)


@expose()
async def user_by_phone(phone, **params):
    """
    Find user by number
    """
    phone = int(phone)
    logger.info('user_by_phone', phone=phone)
    for uid, user in state.users.items():
        if phone == user.phone and user.sess_no:
            return dict(uid=uid, sess_no=user.sess_no)
        logger.warn('sess_no set', uid=uid)


@expose.handler()
async def phone_request(uid='', **params):
    """
    Get allocated phone
    """
    if uid and uid in state.users:
        return dict(num=state.users[uid].phone)


@expose.listener()
async def broadcast(key, name='', uid='', data={}, **params):
    """
    Track events listener to handle activity and sessions
    """
    if uid:
        project_id = data.get('projectId', None)
        now = ms()
        if project_id == settings.project_id:
            if key.startswith('in.gen.track'):
                if name == 'session':
                    sess = pdict.from_dict(data.get('sess', None))
                    phone = rand_item(state.free_phones())
                    if sess and sess.num and phone:
                        # if sess['type'] == 'campaign': and others...
                        # look at session description https://rock.st/docs/reference/web-sdk/sessions/
                        await state.set_user(uid, dict(sess_no=sess['num'], phone=phone, start=now, act=now))
        await state.touch(uid)


async def lease_cleaner():
    while True:
        try:
            for uid in [*state.users.keys()]:
                now = ms()
                user = state.users[uid]
                # Has required attrtibutes
                if user.act and user.start:
                    # Less then 5 min from last activity
                    if now - user.act < 60*5*1000:
                        # Less then 5 min from lease
                        if now - user.start < 60*15*1000:
                            continue
                await state.rm_user(uid)
        except Exception:
            logger.exception('lease_cleaner ex')
        await asyncio.sleep(5)


@worker()
async def redis_connector():
    state.redis_pool = await redis_factory.create_pool()
    state.users = await state.hgetall()
    logger.info('restoring state', s=state.users)
    await scheduler.spawn(lease_cleaner())
