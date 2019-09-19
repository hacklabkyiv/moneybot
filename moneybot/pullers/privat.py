from aiohttp import ClientSession
import logging
from datetime import datetime
from io import StringIO
from moneybot.base import Transaction, Stats as StatsBase, Puller as BasePuller


class Stats(StatsBase):
    def __init__(self, statements):
        super().__init__()
        for stat in statements:
            for account, stats in stat.items():
                self.data[account] = stats

    def transactions(self, account, real=True, done=True):
        for t in self.data.get(account, []):
            ref = list(t.keys())[0]
            t_fields = t[ref]

            # transaction is real
            if real and t_fields['BPL_FL_REAL'] != 'r':
                continue

            # transaction is done
            if done and t_fields['BPL_PR_PR'] != 'r':
                continue

            yield Transaction(
                reference=ref,
                transaction_type=t_fields['TRANTYPE'],
                sum=t_fields['BPL_SUM'],
                timestamp=datetime.strptime(t_fields['DATE_TIME_DAT_OD_TIM_P'],
                                            '%d.%m.%Y %H:%M:%S'),
                osnd=t_fields['BPL_OSND'],
                sender_account=t_fields['BPL_A_ACC'],
                sender_name=t_fields['BPL_A_NAM']
            )

    def __repr__(self):
        return repr(self.data)


class Puller(BasePuller):
    DATE_FORMAT = '%d-%m-%Y'
    API = 'https://acp.privatbank.ua/api/proxy/transactions?startDate={}&endDate={}'

    def __init__(self, config, **kwargs):
        super().__init__()
        logging.info(f'{self} started')

        self._headers = {
            'User-Agent': 'moneybot',
            'Content-Type': 'application/json;charset=utf8',
            'id': config['id'],
            'token': config['token'],
        }

        self._pull_cfg = {
            'TRANTYPE': 'C',  # pull only credit transactions
        }

    async def pull(self):
        end_date = datetime.today()
        start_date = end_date.replace(day=1)
        api = self.API.format(start_date.strftime(self.DATE_FORMAT),
                              end_date.strftime(self.DATE_FORMAT))

        async with ClientSession() as session:
            async with session.get(api, headers=self._headers) as response:
                response = await response.json()
        self.stats = Stats(response['StatementsResponse']['statements'])
        accounts = list(self.stats.keys())
        logging.info(f'Grabbed info for accounts: {accounts}')

        for a in self.stats.accounts:
            with StringIO() as buf:
                for tr in self.stats.transactions(a):
                    buf.write('{} - {}\n'.format(tr.sum, tr.osnd))

                logging.debug('[{}]\n{}'.format(a, buf.getvalue()))

    def __repr__(self):
        return 'Puller::privat'
