# -*- coding: utf-8 -*-
import json
import time
from mcdreforged.api.all import *
import re
import os

PLUGIN_METADATA = {
    'id': 'DCsBot',
    'version': '1.4.0',
    'name': 'DCsBot',
    'author': [
        'DC_Provide'
    ],
    'link': 'Nope...[doge]',
}

command = [
    '!!bot help',
    '!!bot add',
    '!!bot list',
    '!!bot kd',
    '!!bot addknown',
]
operating_player = ''
operating_step = 0
target_bot = ''
bot = {
    'nick_name': '',
    'id': '',
    'dimension': '',
    'position': '',
    'action': [],
    'delay': [],
    'rotate': '0 0',
}
def clear_bot():
    global bot
    bot = {
        'nick_name': '',
        'id': '',
        'dimension': '',
        'position': '',
        'action': [],
        'delay': [],
        'rotate': '0 0',
    }

def user_pos_getter(server, info, player):
    pos = server.rcon_query("data get entity " + player + " Pos")
    pos = pos[pos.find('[') + 1:pos.find(']')]
    pos = pos.replace("d", '')
    pos = pos.replace(',', '')
    return pos

def use_dim_getter(server, info, player):
    dim = server.rcon_query("data get entity " + info.player + " Dimension")
    dim = dim[dim.find('"') + 1:-1]
    return dim

def command_parser(inp, type, server, info):
    if type == 'basic':
        inp = inp.split(' ')
        '''
        v1.3: 更改了输入机制：
        完整输入： bot_name bot_id x y z dim
        省略维度： bot_name bot_id x y z player_dim
        省略坐标： bot_name bot_id player_pos
        '''
        out = ''
        asu = True
        if len(inp) <= 2:
            inp.append('')
            inp.append('')
            inp.append('')
            out += user_pos_getter(server, info, info.player)
            server.reply(info, "检测到您输入的信息不全，已自动为您补全信息：[假人坐标][假人维度]")
        if len(inp) <= 5:
            inp.append('')
            inp[5] =  use_dim_getter(server, info, info.player)
            asu = False
        if len(inp) == 6 and asu:
            if inp[5] == '0':
                inp[5] = 'minecraft:overworld'
            elif inp[5] == '1':
                inp[5] = 'minecraft:the_end'
            elif inp[5] == '-1':
                inp[5] = 'minecraft:the_nether'
            out += inp[2]
            out += ' '
            out += inp[3]
            out += ' '
            out += inp[4]
        bot['nick_name'], bot['id'], bot['dimension'] = inp[0], inp[1], inp[5]
        bot['position'] = out
    if type == 'action':
        inp = inp.split(' ')
        replace_list = {'c': 'continuous', 'i': 'interval'}
        inp = [replace_list[i] if i in replace_list else i for i in inp]
        out = ''
        for i in inp:
            out += i
            out += ' '
        bot['action'].append(out)
        bot['delay'].append(0)
        return out
def bot_storage():
    '''
    一个假人可以包含如下属性，使用dict来储存：
    {
        nick_name: bot的昵称，展示在文件名上
        id: bot的id
        dimension: bot所在维度，在command_parser中自动转换为minecraft:___
        position: bot所在坐标，使用str表示（更方便）
        action: [
            'a', 'b', ...
        ]: bot执行的动作，用列表表示
        delay: [
            0, 1, 2
        ]: bot执行action的延迟，用列表表示，一个action对应一个delay
    }
    :return: None
    '''
    f = open('./DC_Bot/' + bot['nick_name'], 'w')
    f.write(str(bot))
    f.close()

def on_load(server, info):
    try:
        os.listdir(os.getcwd()+ '\\DC_Bot')
    except:
        try:
            os.mkdir(os.getcwd() + '\\DC_Bot')
        except:
            pass
        server.say("ok")
def add_bot(server, info, not_outto = True):
    global operating_player, operating_step, bot
    if info.content == '!!bot add':
        server.say('您已进入假人编辑模式，'+RText(" §4[退出]").c(RAction.run_command, "exit").h('点我退出'))
        operating_player = info.player
        operating_step = 1
        server.reply(info, "请输入假人的昵称 假人id 假人坐标 假人维度")
        server.reply(info, "其中，假人的坐标若不设定默认为玩家坐标")
        server.reply(info, "其中，假人维度：主世界=0，地狱=-1，末地=1，若不设定默认为玩家所在维度")
        server.reply(info, "举例：大程的假人 §eDC_bot §d100 10 100 1")
    elif operating_step == 1 and operating_player == info.player:
        if info.content == "exit":
            server.reply(info, "§4操作被取消！")
            clear_bot()
            operating_step = 0
            operating_player = None
            return
        if not_outto:
            command_parser(info.content, 'basic', server, info)
        server.reply(info, "接下来，请指定假人的动作，与carpet中的假人动作一致")
        server.reply(info, "特别的是：c = continuous, i = interval")
        server.reply(info, "你还可以在命令之前添加§b[num]§f来指定延迟§bnum§f秒后执行该动作")
        server.reply(info, "您可以添加无限多的动作，如果没有动作，输入§e'...'§f来结束")
        server.reply(info, "如果您出错了," + RText(" §4[退出]").c(RAction.run_command, "regret").h('点我反悔'))
        operating_step = 2

    elif operating_step == 2 and operating_player == info.player:
        if info.content == '...':
            operating_step = 0
            server.reply(info, "假人添加成功，假人信息：§7" + str(bot))
            server.reply(info, "您可以添加无限多的动作，如果没有动作，输入§e'...'§f来结束")
            bot_storage()
            clear_bot()
        elif info.content == 'regret':
            operating_step = 0
            operating_player = None
            server.reply(info, "§4操作被取消")
            return
        else:
            inp = command_parser(info.content, 'action', server, info)
            server.reply(info, "成功录入动作：§b" + inp)

def add_known_bot(server, info):
    global operating_step, operating_player, bot
    if info.content.find('!!bot addknown') != -1:
        operating_player = info.player
        operating_step = 101
        server.reply(info, "请输入假人§b名字：")
    elif operating_step == 101 and operating_player == info.player:
        server.reply(info, "添加假人§2成功！")
        server.reply(info, "记录假人§e" + info.content)
        # dim = server.rcon_query("data get entity " + info.content + " Dimension")
        # bot['dimension'] = dim[dim.find('"') + 1:-1]
        bot['dimension'] = use_dim_getter(server, info, info.content)
        # pos = server.rcon_query("data get entity " + info.content + " Pos")
        # pos = pos[pos.find('[')+1:pos.find(']')]
        # pos = pos.replace("d", '')
        bot['position'] = user_pos_getter(server, info, info.content)
        bot['nick_name'] = info.content
        bot['id'] = info.content
        rot = server.rcon_query("data get entity "+info.content+" Rotation")
        rot = rot[rot.find('[') + 1:rot.find(']')]
        rot = rot.replace("f", '')
        bot["rotate"] = rot.replace(",", '')
        server.reply(info, "是否要进行§b动作设置？（包括玩家视角位置）"+
                     RText(" §2[执行]").c(RAction.run_command, "yes").h('点我执行') +
                     RText(" §2[不执行]").c(RAction.run_command, "no").h('点我执行'))
        operating_step = 102
    elif operating_step == 102 and operating_player == info.player:
        if info.content == 'yes':
            operating_step = 1
            add_bot(server, info, not_outto=False)
        else:
            server.reply(info, "§4不进行动作设置")
            f = open('./DC_Bot/' + bot['nick_name'], 'w')
            f.write(str(bot))
            f.close()
            clear_bot()
            operating_step = 0
            operating_player = None
def help_bot(server, info):
    if info.content == '!!bot help':
        server.say("============DC's bot 显示帮助=================")
        server.say("!!bot help §b显示帮助" + RText(" §2[执行]").c(RAction.run_command, command[0]).h('点我执行'))
        server.say("!!bot add §b添加假人" + RText(" §2[执行]").c(RAction.run_command, command[1]).h('点我执行'))
        server.say("!!bot list §bbot列表" + RText(" §2[执行]").c(RAction.run_command, command[2]).h('点我执行'))
        server.say("!!bot kuaidi/!!bot kd §b快递" + RText(" §2[执行]").c(RAction.run_command, command[3]).h('点我执行'))
        server.say("!!bot knownbot  §b添加当前在线的假人到假人列表中" + RText(" §2[执行]").c(RAction.run_command, command[4]).h('点我执行\n'+
                                                                                                                  '这会自动记住假人的当前§e位置§f和§e方向§f以便下次放置' +
                                                                                                                  '\n但是请§c注意§f：假人的§c动作§f不会被记录在内'))
def list_bot(server, info):
    if info.content == '!!bot list' or info.content == '!!bot':
        server.reply(info, "==========DC's bot 假人列表=======" + RText(" §6[命令列表]").c(RAction.run_command, command[0]).h('点我执行'))
        fold_list = os.listdir(os.getcwd() + '\\DC_Bot')
        for i in fold_list:
            server.reply(info, i +
                       RText(" §2[√]").c(RAction.run_command, '!!bot on ' + i).h('点我挂§b'+i) +
                       RText(" §4[×]").c(RAction.run_command, '!!bot off '+i).h('点我卸载§b'+i)+
                       RText(" §5[E]").c(RAction.run_command, '!!bot edit '+i).h('点我编辑§b'+i+'§f的详细信息')+
                       RText(" §6[R]").c(RAction.run_command, '!!bot remove '+i).h('点我删除§b'+i) +
                       RText(" §b[I]").c(RAction.run_command, '!!bot info ' + i).h('点我查询§b' + i + "§f的详细信息")
                       )
    return
def join_bot(server, info):
    f = open('./DC_Bot/'+info.content[9:], 'r')
    bot_info = eval(f.read())
    server.execute("execute in "+ bot_info['dimension']+ " run player "+ bot_info["id"] + " spawn at " + bot_info["position"])
    server.say(
        "execute in " + bot_info['dimension'] + " run player " + bot_info["id"] + " spawn at " + bot_info["position"])
    server.execute("player "+bot_info['id']+" look "+bot_info["rotate"])
    server.say("player " + bot_info['id'] + " look " + bot_info["rotate"])
    for i in bot_info['action']:
        server.execute("player " + bot_info['id'] + ' ' + i[:-1])
        time.sleep(1)
    f.close()
def kill_bot(server, info):
    f = open('./DC_Bot/' + info.content[10:], 'r')
    bot_info = eval(f.read())
    server.execute("execute at "+ bot_info['id'] +" run forceload add ~ ~")
    server.execute("player " + bot_info['id'] + " sneak")
    time.sleep(1)
    server.execute('player '+ bot_info['id'] + ' kill')
    time.sleep(15)
    server.execute("execute in " +bot_info['dimension'] + " run forceload remove all")
def remove_bot(server, info):
    global operating_player, operating_step, target_bot
    if info.content.find("!!bot remove") != -1:
        server.reply(info, "您确定要执行此操作吗？")
        server.reply(info, info.content[13:] + "将会失去很久(真的很久！)")
        server.reply(info,
                     RText(" §2[√]").c(RAction.run_command, '!!bot confirm').h('肘你！删了算了') +
                     RText(" §4[×]").c(RAction.run_command, '!!bot abort').h('抱歉，点戳了')
                     )
        operating_step = 201
        operating_player = info.player
        target_bot = info.content[13:]
    elif operating_step == 201 and operating_player == info.player:
        if info.content == '!!bot confirm':
            server.say("[悲报]" + target_bot + "永远离我们而去了!")
            os.remove(os.getcwd() + "\\DC_Bot\\" + target_bot)
        else:
            server.reply(info, "我也知道是你手贱点错了，对吧~")
        operating_player = None
        operating_step = 0
def edit_bot(server, info):
    server.reply(info, "对不起，该功能仍处于Debug中...")
    server.reply(info, "进入bot: " + info.content[11:] + "的编辑模式")
    server.reply(info, RText(" §2[基本信息]").c(RAction.run_command, '!!bot edit_basic ' + info.content[11:]).h('编辑基本信息')+
                 RText(" §3[编辑动作]").c(RAction.run_command, '!!bot on ' + i).h('点我挂'+i))

def kuaidi(server, info):
    global operating_player, operating_step, target_bot
    if info.content == "!!bot kuaidi" or info.content == "!!bot kd":
        server.execute("execute at "+info.player + " run player kuaidi spawn")
        server.reply(info, "您现在可以" + RText(" §2[指定收信人]§f").c(RAction.run_command, '!!bot goto').h('指定收信人')+
                     "或者" + RText(" §4[直接寄快递]§f").c(RAction.run_command, '!!bot delfp').h('寄出快递'))
    if info.content == "!!bot goto":
        operating_step = 301
        operating_player = info.player
        server.reply(info, "请输入收信人，不用完全匹配，比如DC_Provide可以输入DC（区分大小写）")
    elif operating_step == 301 and operating_player == info.player:
        a = server.rcon_query("list")
        #server.say(a)
        a = a[a.find(":") + 2:]
        a = a.split(', ')
        #server.say(str(a))
        for i in a:
            if i.find(info.content)!= -1:
                server.reply(info, "找到了收信人" + i)
                target_bot = i
                server.reply(info, RText(" §2[点我寄快递]§f").c(RAction.run_command, '!!bot gotok').h('寄出快递'))
        operating_step = 0
        operating_player = None
    if info.content == '!!bot gotto':
        server.execute("player kuaidi kill")
        time.sleep(1)
        server.execute("execute at " + target_bot + " run player kuaidi spawn")
        server.execute("player kuaidi look down")
        time.sleep(1)
        server.execute("player kuaidi dropStack all")
        server.execute("player kuaidi kill")
    if info.content == '!!bot delfp':
        server.say("§b" + info.player + "§f寄出了一个快递！" +
                   RText(" §2[点我收快递]§f").c(RAction.run_command, '!!bot accept').h('收快递'))
    if info.content == '!!bot accept':
        server.reply(info, "§2钉~您的快递已送达")
        server.execute("player kuaidi kill")
        time.sleep(1)
        server.execute("execute at " + info.player + " run player kuaidi spawn")
        server.execute("player kuaidi look down")
        time.sleep(1)
        server.execute("player kuaidi dropStack all")
        server.execute("player kuaidi kill")
    if info.content == '!!bot gotok':
        server.say("§b" + info.player + "§f向§b" + target_bot + "§f发送了一个快递！" +
                   RText(" §2[点击将快递送达/收快递]§f").c(RAction.run_command, '!!bot gotto').h('收快递\n非收信人也可以点击这个按钮将当前的快递寄给收信人!!'))
def info_bot(server, info):
    if info.content.find("!!bot info") != -1:
        try:
            server.say("有关bot: §b" + info.content[11:] + "§f的信息:")
            f = open('./DC_Bot/' + info.content[11:], 'r')
            bot_info = f.read()
            bot_info = eval(bot_info)
            server.reply(info, "假人位置：§a" + bot_info['position'])
            server.reply(info, "假人维度：§b" + bot_info['dimension'])
            server.reply(info, "假人动作：")
            for i in bot_info['action']:
                server.reply(info, "§6-§f " + i)
            if len(bot_info['action']) == 0:
                server.reply(info, "§9那啥，假人没动作，空空如也~")
            i = bot_info['nick_name']
            server.reply(info, "对于这个假人，您可以执行如下操作：\n" +
                         RText(" §2[挂假人]").c(RAction.run_command, '!!bot on ' + bot_info['nick_name']).h('点我挂§b' + bot_info['nick_name']) +
                         RText(" §4[卸载假人]").c(RAction.run_command, '!!bot off ' + bot_info['nick_name']).h('点我卸载§b' + i) +
                         RText(" §5[编辑假人]").c(RAction.run_command, '!!bot edit ' + bot_info['nick_name']).h('点我编辑§b' + i + '§f的详细信息') +
                         RText(" §6[删除假人]").c(RAction.run_command, '!!bot remove ' + bot_info['nick_name']).h('点我删除§b' + i)
                         )
        except:
            server.reply(info, "§4[错误] §f没有找到 bot §b" + info.content[11:] + "§f, 请重新检查您的输入")

def user_parser(server, info):
    if info.content.find("!!bot on") != -1:
        #挂bot
        server.reply(info, "正在挂bot")
        join_bot(server, info)
    if info.content.find("!!bot off") != -1:
        #杀bot
        server.reply(info, "正在卸载bot，卸载后会给予其所在区块15秒的加载时长")
        kill_bot(server, info)
    if info.content.find("!!bot edit") != -1:
        #编辑bot
        edit_bot(server, info)


def on_user_info(server, info):
    global operating_player, operating_step
    help_bot(server, info)
    add_bot(server, info)
    add_known_bot(server, info)
    list_bot(server, info)
    remove_bot(server, info)
    info_bot(server, info)
    kuaidi(server, info)
    if info.content[0:5] =='!!bot':
        user_parser(server, info)
    elif info.content == '!!color':
        server.say("§1[1]§2[2]§3[3]§4[4]§5[5]§6[6]§7[7]§8[8]§9[9]§0[0]§a[a]§b[b]§c[c]§d[d]§e[e]§f[f]")
        server.say("§k[1]123§q")
