"""
A DB migration tool.
The tool is based on tortoise `aerich` which is tortoise's own DB migration utility.
By wrapping the aerich here, into our own tool, we aim to provide a simple and easy to use tool that does not require
you to set up and learn aerich.
"""

import asyncio
from typing import List
import argparse
from aerich import Command

from torpedo.common_utils import json_file_to_dict

config = json_file_to_dict("./config.json")


# Arguments parsing
parser = argparse.ArgumentParser(
    prog='python3 database.py',
    description='Used to manage the DB migrations and 1st time schema setup',
    epilog='Text at the bottom of help'
)

parser.add_argument(
    'command',
    choices=["init_db", "heads", "history", "inspectdb", "downgrade", "upgrade", "migrate"],
    help='Command to be executed'
)
#

parser.add_argument('-n', '--name', help="New migration file name. To be used with the `migrate` command")
parser.add_argument('-t', '--tables', nargs='+', help="List of tables. To be used with the `inspectdb` command")
parser.add_argument('-mv', '--migration-version', help="Migration version. To be used with the `downgrade` command")

args = parser.parse_args()


async def init():
    tortoise_config = config['DB_CONNECTIONS']
    tortoise_config['apps']['notification_core']['models'].append('aerich.models')
    command = Command(tortoise_config=tortoise_config, app='notification_core')
    await command.init()
    return command


async def init_db():
    """
    Generate schema and generate app migrate location.
    """
    command = await init()
    resp = await command.init_db(True)
    return resp


async def heads():
    """
    Show current available heads in migrate location.
    """
    command = await init()
    resp = await command.heads()
    return resp


async def history():
    """
    List all migrate items
    """
    command = await init()
    resp = await command.history()
    return resp


async def inspectdb(tables: List[str] = None):
    """
    Introspects the database tables to standard output.
    Used to generate model classes from database.
    """
    command = await init()
    resp = await command.inspectdb(tables=tables)
    return resp


async def downgrade(version: int, delete: bool):
    """
    Downgrade to specified version
    """
    command = await init()
    resp = await command.downgrade(version=version, delete=delete)
    return resp


async def upgrade():
    """
     Upgrade to the latest version.
     The operation of transactional in nature.
    """
    command = await init()
    resp = await command.upgrade(True)
    return resp


async def migrate(name: str = "update"):
    """
    Generate migrate changes file
    """
    command = await init()
    resp = await command.migrate(name=name)
    return resp


async def main():
    # argparse.as
    command = args.command
    if command == 'heads':
        resp = await heads()
    elif command == 'history':
        resp = await history()
    elif command == 'inspectdb':
        tables = args.tables or None
        resp = await inspectdb(tables)
    elif command == 'upgrade':
        resp = await upgrade()
    elif command == 'downgrade':
        m_version = args.migration_version
        if not m_version:
            raise Exception("Provide the migration version to be downgraded!")
        resp = await downgrade(m_version)
    elif command == 'migrate':
        name = args.name or None
        resp = await migrate(name)
    elif command == 'init_db':
        await init_db()
        resp = "Schema created successfully!"
    else:
        raise Exception("Invalid command")

    print("##################Response######################\n")
    print(resp)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())