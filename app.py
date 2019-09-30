
import os
import asyncio
import aiomisc
import yaml
import logging
import logging.config
import importlib
from datetime import datetime
from pprint import pformat


class Moneybot:
    """An aggregator for the main routine"""
    def __init__(self, config):
        self._config = config

        self.pullers = []
        for p in ('privat',):
            cc = config['pullers'][p]
            pp = importlib.import_module(f'moneybot.pullers.{p}').Puller(
                cc, prefix=config['db_prefix'],
                monthly_donate=config['monthly_donate'])
            self.pullers.append(pp)

        self.pushers = []
        for p in ('slack', 'csv'):
            cc = config['pushers'][p]
            pp = importlib.import_module(f'moneybot.pushers.{p}').Pusher(
                cc, prefix=config['db_prefix'],
                monthly_donate=config['monthly_donate'])
            self.pushers.append(pp)

    async def flow(self):
        """The main loop"""
        while True:
            await asyncio.gather(*[p.pull() for p in self.pullers])

            now = datetime.now()
            await asyncio.gather(*[
                ps.push(pl.stats, now=now, provider=str(pl))
                for pl in self.pullers for ps in self.pushers
            ])

            await asyncio.sleep(self._config['update_interval'])


async def main():
    config = yaml.safe_load(open('config.yml', 'r'))
    logging_config = yaml.safe_load(open('logging.yml', 'r'))
    logging_config['root']['level'] = config['log_level']

    logging.config.dictConfig(logging_config)
    logging.debug('Config: {}'.format(pformat(config)))

    db_prefix = config['db_prefix']
    if not os.path.exists(f'./{db_prefix}'):
        os.mkdir(db_prefix)

    mb = Moneybot(config)
    await mb.flow()


with aiomisc.entrypoint() as loop:
    loop.run_until_complete(main())
