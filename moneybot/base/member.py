from dataclasses import dataclass
import typing as t
import logging


@dataclass(frozen=True, repr=True)
class RealName:
    name: str
    surname: str


@dataclass(order=True, frozen=True, repr=True)
class Member:
    """Class for a slack/hackerspace member"""
    slack_id: str
    slack_nickname: str
    payment_tokens: t.List[RealName]
    donator: bool


def get_members(config_members, slack_users) -> t.List[Member]:
    """Get all the Slack users. Filter out bots and deleted ones."""
    recognized = []
    for u in slack_users:
        u_id = u['id']
        if u.get('deleted', False) or u.get('is_bot', False):
            logging.debug(f'Skip user {u_id} due to one is bot or deleted')
            continue

        if u_id not in config_members:
            logging.warning(f'No config for user {u_id}')
            continue

        names = config_members.get('names')
        if names is None:
            logging.warning(f'Invalid config for user {u_id}')
            continue

        nickname = config_members.get('nickname', u['name'])
        donator = config_members.get('donator', False)

        m = Member(payment_tokens=[n.lower() for n in names],
                   slack_id=u_id,
                   slack_nickname='@' + nickname,
                   donator=donator)
        recognized.append(m)
    return recognized
