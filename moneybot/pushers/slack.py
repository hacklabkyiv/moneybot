import logging
from datetime import datetime, time
import plyvel
import os
import slack
import typing as t
from pprint import pformat

from moneybot.base import Stats, Pusher as BasePusher, get_members, Member


def next_fire_dt(now: datetime, remind_day: int, remind_time: time) -> datetime:
    """Calculate the next fire time."""
    return now.replace(day=remind_day,
                       hour=remind_time.hour,
                       minute=remind_time.minute,
                       second=0,
                       microsecond=0)


def calc_user_donations(member: Member, stats: Stats) -> float:
    """Calculate user donations from given monthly stats."""
    user_donations = 0.0
    for a in stats.accounts:
        for tr in stats.transactions(a):
            ll = tr.osnd.lower()
            pt = member.payment_tokens
            if member.slack_nickname in ll or any(n in ll for n in pt):
                user_donations += float(tr.sum)
                tr.member_nickname = member.slack_nickname

    return user_donations


class FireStorage:
    """A wrapper for leveldb that keeps track on fired notifications."""
    def __init__(self, prefix):
        db_path = f'./{prefix}/pushers'
        if not os.path.exists(db_path):
            os.mkdir(db_path)

        # user/channel name -> timestamp
        self.db = plyvel.DB(db_path + '/slack', create_if_missing=True)

    def fired(self, channel: str, fire_time: datetime) -> bool:
        """Has a notification been fired for channel and datetime?"""
        dt = self.get_dt(channel)
        if dt is None:
            return False
        return dt >= fire_time.timestamp()

    def get_dt(self, channel: str) -> t.Optional[float]:
        """Get the last fired time for the channel."""
        dt = self.db.get(bytes(channel, 'utf-8'))
        if dt is None:
            return None
        return float(str(dt, 'utf-8'))

    def set_dt(self, channel: str, fire_time: datetime):
        """Set the last fired time for the channel."""
        self.db.put(bytes(channel, 'utf-8'),
                    bytes(str(fire_time.timestamp()), 'utf-8'))


class Pusher(BasePusher):
    """Slack reminder for general and private messages."""

    def __init__(self, config, prefix, monthly_donate, **kwargs):
        logging.info(f'{self} started')

        self.d = monthly_donate
        self.e = ':{}:'.format(config['emoji'])

        self.s = FireStorage(prefix)

        time_fmt = '%H:%M'
        now = datetime.now()
        self.general_rt = next_fire_dt(
            now,
            config['general_date'],
            datetime.strptime(config['general_time'],
                              time_fmt).time()
        )
        self.private_rt = next_fire_dt(
            now,
            config['private_date'],
            datetime.strptime(config['private_time'],
                              time_fmt).time()
        )

        self.general_text = config['general_text'].format(price=self.d,
                                                          emoji=self.e)
        self.private_text = config['private_text']

        self.g = '#general'
        self.client = slack.WebClient(token=config['token'], run_async=True)
        self._members = None
        self._config_members = config['members']

    async def _get_members(self):
        if self._members is None:
            r = await self.client.users_list()
            slack_users = r['members']
            self._members = get_members(self._config_members, slack_users)
            logging.info('Recognized users:\n{}'.format(pformat(self._members)))
        return self._members

    async def pm(self, member: Member, part: float, fire_time: datetime):
        """Send a private message."""
        logging.info(f'Posting message for {member}')
        msg = self.private_text.format(username=member.slack_nickname,
                                       price=self.d,
                                       part=part,
                                       emoji=self.e)
        response = await self.client.chat_postMessage(
            channel=member.slack_id, text=msg, as_user=True, link_names=True)
        if not response['ok']:
            logging.error(f'Failed to notify {member}')
            return
        self.s.set_dt(member.slack_id, fire_time)

    async def general(self, fire_time: datetime):
        """Send a #general reminder."""
        logging.info(f'Posting message for {self.g}')
        response = await self.client.chat_postMessage(
            channel=self.g, text=self.general_text,
            as_user=True, link_names=True)
        if not response['ok']:
            logging.error('Failed to notify #general')
            return
        self.s.set_dt(self.g, fire_time)

    async def push(self, stats: Stats, **kwargs):
        logging.info(f'{self} reminders')

        now = kwargs['now']
        self.general_rt = self.general_rt.replace(month=now.month)
        self.private_rt = self.private_rt.replace(month=now.month)

        if self.general_rt <= now and not self.s.fired(self.g, self.general_rt):
            await self.general(self.general_rt)

        members = await self._get_members()
        if members is not None and self.private_rt <= now:
            for m in members:
                if self.s.fired(m.slack_id, self.private_rt):
                    continue

                user_donations = calc_user_donations(m, stats)
                if user_donations < self.d:
                    await self.pm(m, user_donations, self.private_rt)

    def __repr__(self):
        return 'Reminder::slack'
