# -*- coding:utf-8 -*-
import re
import requests
import urllib.parse
from collections import OrderedDict
import xbmcplugin, xbmcgui
import json

# plugin config
_plugin_name = '哆啦搜索'
_plugin_handle = int(sys.argv[1])  # 当前句柄
_plugin_address = sys.argv[0]  # 当前插件地址
_plugin_parm = sys.argv[2]  # 问号以后的内容
_plugin_dialog = xbmcgui.Dialog()
print('duola:' + str(_plugin_handle), _plugin_address, _plugin_parm)

# bot config
Site_url ='https://a1.m1907.cn/api/v/?z=80cbcae8041527fc77204d82c3c725fd&jx='
UA_head = { 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
 }

# 【特定函数】
def check_json(input_str):
    try:
        json.loads(input_str)
        return True
    except:
        return False

# 【获取推荐】
def Bot_load_menu():
    url = Site_url + '/'
    res = requests.get(url, headers=UA_head)
    code = res.text
    re_z = re.compile(r'<li><a.href=./hanju/(.*?).>(.*?)</a>')  # 正则
    types = re_z.findall(code)
    if len(types) > 0:
        for type in types:
            # 构造带问号的kodi专属插件url地址，便于识别，?kodi_type=/type1001.html
            type_url = '?kodi_type=' + type[0]
            type_name = type[1]
            # KODI代码嵌入开始
            listitem = xbmcgui.ListItem(type_name)
            xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address + type_url, listitem, True)
            # KODI代码嵌入完毕
    else:
        print('duola_debug:暂无电影分类列表提供')


    # python2中遍历字典时键值对返回的顺序与存储顺序不同，而python3.6+则更改了字典算法会自动按照存储顺序排序，因此此处定义字典为OrderedDict对象
    play_list = OrderedDict()
    url = Site_url + urllib.parse.unquote(detail_url)
    res1 = requests.get(url, headers=UA_head)
    res1.encoding = Site_encoding
    text = res1.text
    text2 = re.search(r'<ul.class="stui-content__playlist.clearfix".+?</ul>', text)
    play_text = text2.group()
    gz1 = re.compile(r'<li.><a.href="(.+?)">(.+?)</a>\s*</li>')
    p_lists = gz1.findall(play_text)
    if len(p_lists) > 0:
        for v_card in p_lists:
            # 提取播放名称，此处为中文，会被系统转换为unicode存储
            v_play_title = v_card[1] + u'[COLOR yellow]【播放地址】[/COLOR]'
            # 构造kodi视频播放地址 ?kodi_play=/video_play/174362/7.html
            v_play_url = '?kodi_play=' + v_card[0]
            play_list[v_play_title] = v_play_url
    else:
        print('duola_debug:本视频暂无播放地址')
        play_list.clear()
    return play_list

# 搜索视频
def Bot_load_search(keyword):
    so_url = Site_url + keyword + '&s1ig=11400&g='
    res = requests.get(url=so_url,headers=UA_head)
    print('duola_debug:'+so_url, 'html_res:'+res.text)
    if check_json(res.text):
        so_json = json.loads(res.text)
        if so_json['type'] == 'movie' or so_json['type'] == 'tv':
            if len(so_json['data']) > 0:
                for vod in so_json['data']:
                    print(vod['name'], vod['year'])
                    vod_title = '[COLOR yellow]《' + vod['name'] + '》[/COLOR] '
                    i = 0
                    for play in vod['source']['eps']:
                        i = i + 1
                        list_item = xbmcgui.ListItem(vod_title + play['name'])
                        # list_item.setArt({'thumb': '123.JPG'})
                        # list_item.setInfo('video', {'year': vod['year'], 'title':vod['name'], 'episodeguide': play['name'], 'tracknumber': i})
                        xbmcplugin.addDirectoryItem(_plugin_handle, play['url'], list_item, False)
                    xbmcplugin.endOfDirectory(handle=_plugin_handle, succeeded=True, updateListing=False, cacheToDisc=True)
            else:
                print('duola_debug:找不到播放地址')
                _plugin_dialog.notification(heading=_plugin_name, message='抱歉，找不到播放列表', time=3000)
        else:
            print('duola_debug:找不到内容')
            _plugin_dialog.notification(heading=_plugin_name, message='抱歉，找不到相关内容', time=3000)
    else:
        print('duola_debug:目标服务器返回的数据无法解析')
        _plugin_dialog.notification(heading=_plugin_name, message='抱歉，目标服务器返回的数据无法解析，服务咱不可用', time=3000)

# 搜索交互
def bot_start_search():
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('请输入关键词')
    keyboard.doModal()
    # xbmc.sleep(1500)
    if keyboard.isConfirmed():
        keyword = keyboard.getText()
        if len(keyword) < 1:
            # https://codedocs.xyz/xbmc/xbmc/group__python___dialog.html#gaa2e71498b420cb4f58e82a467f27c659
            msgbox = _plugin_dialog.ok(_plugin_name, '您必须输入关键词才可以搜索相关内容')
    else:
        keyword = ''
    print('duola_debug:' + keyword)
    if len(keyword) > 0:
        Bot_load_search(keyword)

# 当前选择> 首页
if _plugin_parm == '':
    # https://codedocs.xyz/xbmc/xbmc/group__python___dialog.html#ga27157f98dddb21b44cc6456137977aa2
    #_plugin_dialog.notification(_plugin_name,'欢迎使用'+_plugin_name, xbmcgui.NOTIFICATION_INFO, 3000, False)
    # listitem=xbmcgui.ListItem('[COLOR yellow]哆啦搜索[/COLOR]')
    # xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address+'?kodi_search=yes', listitem, True)
    bot_start_search()

# 当前选择> 搜索
if '?kodi_search=yes' in _plugin_parm:
    print('duola_debug:search>' + _plugin_parm)
    bot_start_search()

# 退出Kodi菜单布局
xbmcplugin.endOfDirectory(_plugin_handle)