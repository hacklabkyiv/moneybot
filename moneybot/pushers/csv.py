import logging
import csv
import os
from datetime import datetime
from moneybot.base import Pusher as BasePusher, Transaction
import typing as t


def format_csv(tr: Transaction) -> t.List:
    """Format a transaction for CVS storage."""
    return [str(i) for i in (
        tr.timestamp,
        tr.transaction_type,
        tr.sum,
        tr.osnd,
        tr.sender_account,
        tr.sender_name,
    )]


class Pusher(BasePusher):
    def __init__(self, config, **kwargs):
        logging.info(f'{self} started')
        self.config = config

        self.d = './' + config['directory']
        if not os.path.exists(self.d):
            os.mkdir(self.d)

    async def push(self, stats, **kwargs):
        provider = kwargs['provider'].split('::')[1]
        logging.info(f'Pushing to {self} from {provider}')

        now = datetime.now()
        filename = self.config['file_format'].format(
            year=now.year,
            month=now.month,
            provider=provider
        )

        with open(os.path.join(self.d, filename), 'w') as out:
            csvout = csv.writer(out)

            for a in stats.accounts:
                for tr in stats.transactions(a):
                    csvout.writerow(format_csv(tr))

    def __repr__(self):
        return 'Pusher::csv'
