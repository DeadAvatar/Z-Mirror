from bot import CMD_INDEX

class _BotCommands:
    def __init__(self):
        self.StartCommand = f'start{CMD_INDEX}'
        self.LeechCommand = (f'leech{CMD_INDEX}', f'l{CMD_INDEX}')
        self.UnzipLeechCommand = (f'unzipleech{CMD_INDEX}', f'uzl{CMD_INDEX}')
        self.ZipLeechCommand = (f'zipleech{CMD_INDEX}', f'zl{CMD_INDEX}')
        self.QbLeechCommand = (f'qbleech{CMD_INDEX}', f'ql{CMD_INDEX}')
        self.QbUnzipLeechCommand = (f'qbunzipleech{CMD_INDEX}', f'quzl{CMD_INDEX}')
        self.QbZipLeechCommand = (f'qbzipleech{CMD_INDEX}', f'qzl{CMD_INDEX}')
        self.YtdlLeechCommand = (f'ytdl{CMD_INDEX}', f'yl{CMD_INDEX}')
        self.YtdlZipLeechCommand = (f'ytdlzip{CMD_INDEX}', f'yzl{CMD_INDEX}')
        self.CancelMirror = f'cancel{CMD_INDEX}'
        self.CancelAllCommand = f'cancelall{CMD_INDEX}'
        self.StatusCommand = f'status{CMD_INDEX}'
        self.AuthorizedUsersCommand = f'users{CMD_INDEX}'
        self.AuthorizeCommand = f'authorize{CMD_INDEX}'
        self.UnAuthorizeCommand = f'unauthorize{CMD_INDEX}'
        self.AddSudoCommand = f'addsudo{CMD_INDEX}'
        self.RmSudoCommand = f'rmsudo{CMD_INDEX}'
        self.PingCommand = f'ping{CMD_INDEX}'
        self.RestartCommand = f'restart{CMD_INDEX}'
        self.StatsCommand = f'stats{CMD_INDEX}'
        self.HelpCommand = f'help{CMD_INDEX}'
        self.LogCommand = f'log{CMD_INDEX}'
        self.ShellCommand = f'shell{CMD_INDEX}'
        self.EvalCommand = f'eval{CMD_INDEX}'
        self.ExecCommand = f'exec{CMD_INDEX}'
        self.ClearLocalsCommand = f'clearlocals{CMD_INDEX}'
        self.LeechSetCommand = f'leechset{CMD_INDEX}'
        self.SetThumbCommand = f'setthumb{CMD_INDEX}'
        self.BtSelectCommand = f'btsel{CMD_INDEX}'
        self.SleepCommand = f'sleep{CMD_INDEX}'

BotCommands = _BotCommands()
