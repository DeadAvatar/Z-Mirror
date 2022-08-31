from signal import signal, SIGINT
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from telegram.ext import CommandHandler
from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, LOGGER, Interval, INCOMPLETE_TASK_NOTIFIER, DB_URI, alive, app, main_loop, AUTHORIZED_CHATS
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .modules import authorize, cancel_mirror, mirror_status, mirror_leech, ytdlp, shell, eval, leech_settings, bt_select, sleep

def progress_bar(percentage):
    p_used = '⬢'
    p_total = '⬡'
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage=int(percentage)
    except:
        percentage = 0
    return ''.join(
        p_used if i <= percentage // 10 else p_total for i in range(1, 11)
    )

def stats(update, context):
    if ospath.exists('.git'):
        last_commit = check_output(["git log -1 --date=short --pretty=format:'%cr \n<b>Version: </b> %cd'"], shell=True).decode()
    else:
        last_commit = 'No UPSTREAM_REPO'
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=1)
    memory = virtual_memory()
    mem_p = memory.percent
    stats = f'<b><i><u>Bot Statistics</u></i></b>\n\n'\
            f'<b>CPU</b>:  {progress_bar(cpuUsage)} {cpuUsage}%\n' \
            f'<b>RAM</b>: {progress_bar(mem_p)} {mem_p}%\n' \
            f'<b>DISK</b>: {progress_bar(disk)} {disk}%\n\n' \
            f'<b>Updated:</b> {last_commit}\n'\
            f'<b>Uptime:</b> <code>{currentTime}</code>\n\n'\
            f'<b>Total Disk:</b> <code>{total}</code> [{disk}% In use]\n'\
            f'<b>Used:</b> <code>{used}</code> | <b>Free:</b> <code>{free}</code>\n'\
            f'<b>T-UL:</b> <code>{sent}</code> | <b>T-DL:</b> <code>{recv}</code>\n'
    sendMessage(stats, context.bot, update.message)

def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("PublicLeechCloneGroup", "https://t.me/PublicLeechCloneGroup")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
Welcome | BOT is ready for you
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMarkup(start_string, context.bot, update.message, reply_markup)
    else:
        sendMarkup('Sorry, You cannot use me', context.bot, update.message, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    alive.kill()
    clean_all()
    srun(["pkill", "-9", "-f", "gunicorn|chrome|firefox|megasdkrest|opera"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update.message)

help_string = f'''
NOTE: Try each command without any perfix to see more detalis.

/{BotCommands.LeechCommand[0]} or /{BotCommands.LeechCommand[1]}: Start leeching to Telegram.

/{BotCommands.ZipLeechCommand[0]} or /{BotCommands.ZipLeechCommand[1]}: Start leeching and upload the file/folder compressed with zip extension.

/{BotCommands.UnzipLeechCommand[0]} or /{BotCommands.UnzipLeechCommand[1]}: Start leeching and upload the file/folder extracted from any archive extension.

/{BotCommands.QbLeechCommand[0]} or /{BotCommands.QbLeechCommand[1]}: Start leeching using qBittorrent.

/{BotCommands.QbZipLeechCommand[0]} or /{BotCommands.QbZipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder compressed with zip extension.

/{BotCommands.QbUnzipLeechCommand[0]} or /{BotCommands.QbUnzipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder extracted from any archive extension.

/{BotCommands.YtdlLeechCommand[0]} or /{BotCommands.YtdlLeechCommand[1]}: Leech yt-dlp supported link.

/{BotCommands.YtdlZipLeechCommand[0]} or /{BotCommands.YtdlZipLeechCommand[1]}: Leech yt-dlp supported link as zip.

/{BotCommands.LeechSetCommand} [query]: Leech settings.

/{BotCommands.SetThumbCommand}: Reply photo to set it as Thumbnail.

/{BotCommands.BtSelectCommand}: Select files from torrents by gid or reply.

/{BotCommands.CancelMirror}: Cancel task by gid or reply.

/{BotCommands.StatusCommand}: Shows a status of all the downloads.

/{BotCommands.StatsCommand}: Show stats of the machine where the bot is hosted in.

'''

def bot_help(update, context):
    sendMessage(help_string, context.bot, update.message)

def main():
    start_cleanup()
    notifier_dict = False
    if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
        if notifier_dict := DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = 'Restarted Successfully!'
                else:
                    msg = 'Bot Restarted!'
                for tag, links in data.items():
                     msg += f"\n\n{tag}: "
                     for index, link in enumerate(links, start=1):
                         msg += f" <a href='{link}'>{index}</a> |"
                         if len(msg.encode()) > 4000:
                             if 'Restarted Successfully!' in msg and cid == chat_id:
                                 bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                                 osremove(".restartmsg")
                             else:
                                 try:
                                     bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                                 except Exception as e:
                                     LOGGER.error(e)
                             msg = ''
                if 'Restarted Successfully!' in msg and cid == chat_id:
                     bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                     osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted Successfully!", chat_id, msg_id)
        osremove(".restartmsg")
    elif not notifier_dict and AUTHORIZED_CHATS:
        for id_ in AUTHORIZED_CHATS:
            try:
                bot.sendMessage(id_, "Bot Restarted!", 'HTML')
            except Exception as e:
                LOGGER.error(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Congratulations, Bot Started Sucessfully !")
    signal(SIGINT, exit_clean_up)

app.start()
main()

main_loop.run_forever()
