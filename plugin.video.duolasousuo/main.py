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
                # xbmcplugin.endOfDirectory(handle=_plugin_handle, succeeded=True, updateListing=False, cacheToDisc=True)
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