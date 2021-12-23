# -*- coding:utf-8 -*-
import sys, re, json
import requests
import urllib.parse
from collections import OrderedDict
# https://codedocs.xyz/xbmc/xbmc/
import xbmcplugin, xbmcgui, xbmc

# plugin config
_plugin_name = '哆啦搜索'
_plugin_player_mimes = ['.m3u8','.mp4','.flv','.ts']
_plugin_handle = int(sys.argv[1])  # 当前句柄
_plugin_address = sys.argv[0]  # 当前插件地址
_plugin_parm = sys.argv[2]  # 问号以后的内容
_plugin_dialog = xbmcgui.Dialog()
print('duola_debug:[' + str(_plugin_handle)+']'+ _plugin_address+' || '+ _plugin_parm)

# bot config
Site = 'https://m3u8.xiangkanapi.com'
Site_api_list = Site + '/provide/vod/?ac=list'
Site_api_search = Site + '/provide/vod/?wd='
Site_api_detail = Site + '/provide/vod/?ac=detail&ids='

UA_head = { 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
 }

# 特定函数
def check_json(input_str):
    try:
        json.loads(input_str)
        return True
    except:
        return False
def check_url_mime(url):
    hz = '.' + url.split('.')[-1]
    if hz in _plugin_player_mimes:
        return True
    else:
        return False

# 视频查找：返回符合的视频列表
def Web_load_search(keyword):
    to_url = Site_api_search + keyword
    res = requests.get(url=to_url,headers=UA_head)
    # print('dula_debug:'+to_url, res.text)
    if check_json(res.text):
        res_json = json.loads(res.text)
        if res_json['code'] == 1:
            if len(res_json['list']) > 0:
                for video in res_json['list']:
                    vod_id = str(video['vod_id'])
                    vod_name = '[COLOR yellow]' + video['vod_name'] + '[/COLOR] '
                    vod_remarks = video['vod_remarks']
                    vod_typename = video['type_name']
                    # 建立kodi菜单
                    list_item = xbmcgui.ListItem(vod_name+' ('+ vod_typename+' / '+vod_remarks+')')
                    # list_item.setArt({'icon': '123.JPG'})
                    # list_item.setInfo('video', {'year': vod['year'], 'title':vod['name'], 'episodeguide': play['name'], 'tracknumber': i})
                    xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address+'?kodi_detail='+vod_id, list_item, True)
                # 退出kodi菜单布局
                xbmcplugin.endOfDirectory(handle=_plugin_handle, succeeded=True, updateListing=False, cacheToDisc=True)
            else:
                print('duola_debug:找不到资源')
                _plugin_dialog.notification(heading=_plugin_name, message='抱歉，找不到相关资源', time=3000)
        else:
            print('duola_debug:无法解析json')
            _plugin_dialog.notification(heading=_plugin_name, message='抱歉，由于无法解析返回的数据，服务暂时不可用，请稍后重试', time=3000)
    else:
        print('duola_debug:目标服务器返回的数据无法解析')
        _plugin_dialog.notification(heading=_plugin_name, message='抱歉，目标服务器返回的数据无法响应，服务暂不可用', time=3000)

# 视频内容：返回单个视频详情，并交互输出select play list
def Web_load_detail_one_style1(detail):
    to_url = Site_api_detail + detail
    res = requests.get(url=to_url,headers=UA_head)
    # print('dula_debug:'+to_url, res.text)
    if check_json(res.text):
        res_json = json.loads(res.text)
        if res_json['code'] == 1:
            if len(res_json['list']) > 0:
                video = res_json['list'][0] # 仅提取一个
                v_id = str(video['vod_id'])
                v_name = '[COLOR yellow]' + video['vod_name'] + '[/COLOR] '
                v_remarks = video['vod_remarks']
                v_typename = video['type_name']
                v_picture = video['vod_pic']
                # 第1集$https://v.qq.com/x/1.mp4#第2集$https://v.qq.com/x/2.mp4#第3集$https://v.qq.com/x/3.mp4
                v_list_text = video['vod_play_url'] 
                v_infos = {}
                try:
                    v_infos['title'] = video['vod_name']
                    v_infos['originaltitle'] = video['vod_name']
                    v_infos['tag'] = video['vod_remarks']
                    v_infos['status'] = 'n/a'
                    v_infos['country'] = video['vod_area']
                    v_infos['year'] = video['vod_year']
                    v_infos['director'] = video['vod_director']
                    v_infos['cast'] = video['vod_actor'].split(',')
                    v_infos['plot'] = video['vod_content']
                    v_infos['rating'] = float(video['vod_score'])
                except IndexError as e:
                    pass
                # dialog.select
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                V_name_list = []
                V_m3u8_list = []
                GZ_v = re.compile(r'(.+?)\$(.+?)#')
                play_list = GZ_v.findall(v_list_text)
                if len(play_list) > 0:
                    select_title = v_name + ':请选择播放源开始播放'
                    i = 0
                    for play in play_list:
                        if check_url_mime(play[1]):
                            V_name_list.append(play[0]) # 播放标签
                            V_m3u8_list.append(play[1]) # 播放地址
                            # listitem
                            list_item = xbmcgui.ListItem(v_name + ':' + play[0], v_typename)
                            list_item.setArt({'thumb': v_picture, 'poster': v_picture})
                            list_item.setInfo('video', v_infos)
                            playlist.add(url=play[1], listitem=list_item, index=i)
                            i = i +1
                        else:
                            pass # 不符合条件的播放地址跳过
                else:
                   select_title = '此视频暂时没有播放源'
                # 生成 select
                dialog = xbmcgui.Dialog()
                select_i = dialog.select(select_title, V_name_list)
                print('duola_debug: select_i '+str(select_i))
                if select_i >= 0:
                    # 立即播放单个
                    # xbmc.Player().play(item=V_m3u8_list[select_i], listitem=list_item)
                    # 立即播放列表
                    xbmc.Player().play(item=playlist, listitem=list_item, windowed=False, startpos=select_i)
                    _plugin_dialog.notification(
                        heading = _plugin_name, 
                        message = v_name + ':' + V_name_list[select_i] + ' 即将自动播放，请稍候', 
                        time=5000, 
                        sound=False
                    )
            else:
                print('duola_debug:没有数据')
                _plugin_dialog.notification(heading=_plugin_name, message='抱歉，找不到播放列表', time=3000)
        else:
            print('duola_debug:无法解析json')
            _plugin_dialog.notification(heading=_plugin_name, message='抱歉，由于无法解析返回的数据，服务暂时不可用，请稍后重试', time=3000)
    else:
        print('duola_debug:目标服务器返回的数据无法解析')
        _plugin_dialog.notification(heading=_plugin_name, message='抱歉，目标服务器返回的数据无法响应，服务暂不可用', time=3000)

# 视频内容：返回单个视频详情，并交互输出select play list
def Web_load_detail_one_style2(detail):
    to_url = Site_api_detail + detail
    res = requests.get(url=to_url,headers=UA_head)
    # print('dula_debug:'+to_url, res.text)
    if check_json(res.text):
        res_json = json.loads(res.text)
        if res_json['code'] == 1:
            if len(res_json['list']) > 0:
                video = res_json['list'][0] # 仅提取一个
                v_id = str(video['vod_id'])
                v_name = '[COLOR yellow]' + video['vod_name'] + '[/COLOR] '
                v_remarks = video['vod_remarks']
                v_typename = video['type_name']
                v_picture = video['vod_pic']
                # 第1集$https://v.qq.com/x/1.mp4#第2集$https://v.qq.com/x/2.mp4#第3集$https://v.qq.com/x/3.mp4
                v_list_text = video['vod_play_url'] 
                v_infos = {}
                try:
                    v_infos['title'] = video['vod_name']
                    v_infos['originaltitle'] = video['vod_name']
                    v_infos['tag'] = video['vod_remarks']
                    v_infos['status'] = 'n/a'
                    v_infos['country'] = video['vod_area']
                    v_infos['year'] = video['vod_year']
                    v_infos['director'] = video['vod_director']
                    v_infos['cast'] = video['vod_actor'].split(',')
                    v_infos['plot'] = video['vod_content']
                    v_infos['rating'] = float(video['vod_score'])
                except IndexError as e:
                    pass
                # A方案：dialog
                V_name_list = []
                V_m3u8_list = []
                GZ_v = re.compile(r'(.+?)\$(.+?)#')
                play_list = GZ_v.findall(v_list_text)
                if len(play_list) > 0:
                    select_title = v_name + ':请选择播放源开始播放'
                    for play in play_list:
                        if check_url_mime(play[1]):
                            V_name_list.append(play[0]) # 播放标签
                            V_m3u8_list.append(play[1]) # 播放地址
                        else:
                            pass # 不符合条件的播放地址跳过
                else:
                   select_title = '此视频暂时没有播放源'
                dialog = xbmcgui.Dialog()
                select_i = dialog.select(select_title, V_name_list)
                # 生成 select list
                print('duola_debug: select_i '+str(select_i))
                if select_i >= 0:
                    list_item = xbmcgui.ListItem(v_name, v_typename, V_m3u8_list[select_i], offscreen=False)
                    list_item.setArt({'thumb': v_picture, 'poster': v_picture})
                    list_item.setInfo('video', v_infos)
                    #_plugin_dialog.info(list_item) # 显示视频信息，含播放按钮
                    xbmc.Player().play(item=V_m3u8_list[select_i], listitem=list_item) # 立即播放
                    _plugin_dialog.notification(
                        heading = _plugin_name, 
                        message = v_name + ':' + V_name_list[select_i] + ' 即将自动播放，请稍候', 
                        time = 5000, 
                        sound = False
                    )
                # B方案：Directory
                # list_item = xbmcgui.ListItem(v_name+' (' + v_remarks+' / ' + v_typename + ')')
                # list_item.setArt({'thumb': v_picture})
                # list_item.setInfo('video', v_infos)
                # 建立目录菜单
                # xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address+'?kodi_test=123', list_item, True)
                # 退出目录菜单 布局
                # xbmcplugin.endOfDirectory(handle=_plugin_handle, succeeded=True, updateListing=False, cacheToDisc=True)
            else:
                print('duola_debug:没有数据')
                _plugin_dialog.notification(heading=_plugin_name, message='抱歉，找不到播放列表', time=3000)
        else:
            print('duola_debug:无法解析json')
            _plugin_dialog.notification(heading=_plugin_name, message='抱歉，由于无法解析返回的数据，服务暂时不可用，请稍后重试', time=3000)
    else:
        print('duola_debug:目标服务器返回的数据无法解析')
        _plugin_dialog.notification(heading=_plugin_name, message='抱歉，目标服务器返回的数据无法响应，服务暂不可用', time=3000)

# 搜索交互
def kodi_start_search():
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('请输入关键词')
    keyboard.doModal()
    # xbmc.sleep(1500)
    if keyboard.isConfirmed():
        keyword = keyboard.getText()
        if len(keyword) < 1:
            msgbox = _plugin_dialog.ok(_plugin_name, '您必须输入关键词才可以搜索相关内容')
    else:
        keyword = ''
    print('duola_debug:' + keyword)
    if len(keyword) > 0:
        Web_load_search(keyword)

# 当前路由> 访问首页
if _plugin_parm == '':
    # https://codedocs.xyz/xbmc/xbmc/group__python___dialog.html#ga27157f98dddb21b44cc6456137977aa2
    #_plugin_dialog.notification(_plugin_name,'欢迎使用'+_plugin_name, xbmcgui.NOTIFICATION_INFO, 3000, False)
    listitem=xbmcgui.ListItem('[COLOR yellow]哆啦搜索[/COLOR]')
    xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address+'?kodi_search=yes', listitem, True)
    listitem=xbmcgui.ListItem('使用帮助')
    xbmcplugin.addDirectoryItem(_plugin_handle, _plugin_address+'?kodi_help', listitem, True)
    # 退出kodi菜单布局（如果没有及时退出布局会被Kodi进行布局，而不响应文件夹点击）
    xbmcplugin.endOfDirectory(handle=_plugin_handle, succeeded=True, updateListing=False, cacheToDisc=True)
    # kodi_start_search()

# 当前路由> 访问搜索
if '?kodi_search=yes' in _plugin_parm:
    print('duola_debug:' + _plugin_parm)
    kodi_start_search()

# 当前路由> 访问视频详情
if '?kodi_detail=' in _plugin_parm:
    detail = _plugin_parm.split("kodi_detail=")[1]
    if detail != "":
        this_list = Web_load_detail_one_style1(detail)
    else:
        print('maliao_debug:传入的kodi_detail地址为空')
        _plugin_dialog.notification(heading=_plugin_name, message='此视频信息无效，无法访问此视频', time=3000)