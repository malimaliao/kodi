# -*- coding:utf-8 -*-
import sys, re
import requests
import urllib.parse
from collections import OrderedDict
import xbmcplugin, xbmcgui, xbmc
# https://kodi.wiki/view/Add-on_development

# plugin config
Plugin_name = '韩剧'
Plugin_handle = int(sys.argv[1])  # 当前句柄
Plugin_URL = sys.argv[0]  # 当前插件地址
Plugin_URL_parm = sys.argv[2]  # 问号以后的内容
Plugin_dialog = xbmcgui.Dialog()
print('maliao_debug:' + str(Plugin_handle), Plugin_URL, Plugin_URL_parm)

# api config
Bot_site ='http://www.hanjutt8.cn'  # 接口域名
Bot_site_18 = False  # 不良内容拦截开关
Bot_site_blackwords = '伦理片,情色片'  # 不良内容关键词黑名单
Bot_site_encoding = 'utf-8'
UA_head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
    "Connection": "close"
}

# 【生成频道列表】
def site_make_menu():
    listitem = xbmcgui.ListItem("电影")
    xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + '?kodi_type=/vodtype/1.html', listitem, True)
    listitem = xbmcgui.ListItem("电视")
    xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + '?kodi_type=/vodtype/15.html', listitem, True)
    xbmcplugin.endOfDirectory(Plugin_handle) # kodi 文件目录布局结束，必须结束，否则程序不会停止布局

# 【获取频道列表】
def site_load_menu():
    url = Bot_site + '/'
    res = requests.get(url, headers=UA_head)
    res.encoding = Bot_site_encoding
    code = res.text
    re_z = re.compile(r'<li><a.href=./hanju/(.*?).>(.*?)</a>')  # 正则
    types = re_z.findall(code)
    if len(types) > 0:
        for type in types:
            # 构造带问号的kodi专属插件url地址，便于识别，?kodi_type=/type1001.html
            type_url = '?kodi_type=' + type[0]
            type_name = type[1]
            # KODI代码嵌入开始
            if Bot_site_18 == True:
                if type_name in Bot_site_blackwords:  # 屏蔽少儿不宜频道
                    continue
                else:
                    listitem = xbmcgui.ListItem(type_name)
                    xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + type_url, listitem, True)
            else:
                listitem = xbmcgui.ListItem(type_name)
                xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + type_url, listitem, True)
            xbmcplugin.endOfDirectory(Plugin_handle)
            # KODI代码嵌入完毕
    else:
        print('maliao_debug:暂无电影分类列表提供')
        Plugin_dialog.notification(heading=Plugin_name, message='抱歉，找不到播放列表', time=3000)

# 【获取栏目列表】
def site_load_type(type_url):
    url = Bot_site + urllib.parse.unquote(type_url)
    res = requests.get(url, headers=UA_head)
    res.encoding = Bot_site_encoding
    html_code = res.text
    gz = re.compile(r'stui-vodlist__box">\s*<a.+?href="(.+?)".title="(.+?)">\s*<img.+?src="(.+?)".+?>[\s\S]*?pic-text.text-right">(.+?)</span>')
    videos = gz.findall(html_code)
    if len(videos) > 0:
        for video in videos:
            # 构造带问号的插件网址，以便于后面kodi识别：?kodi_detail=/vod_detail/174606.html
            v_url = '?kodi_detail=' + video[0]
            if 'http' in video[2]:
                v_images = video[2]
            else:
                v_images = Bot_site + video[2]
            v_title = video[1]
            v_note = video[3]
            v_name = v_title + '(' + v_note + ')'
            listitem = xbmcgui.ListItem(v_name)
            listitem.setArt({'thumb': v_images}) # 此设置方法适用于kodi 19+
            xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + v_url, listitem, True)
        xbmcplugin.endOfDirectory(Plugin_handle)
    else:
        print('maliao_debug:暂时无法获取到本栏目下的电影列表')
        Plugin_dialog.notification(heading=Plugin_name, message='暂时无法获取到本栏目下的电影列表', time=3000)

# 【获取电影播放列表】
def site_load_vod_detail(detail_url):
    # python2中遍历字典时键值对返回的顺序与存储顺序不同，而python3.6+则更改了字典算法会自动按照存储顺序排序，因此此处定义字典为OrderedDict对象
    play_list = OrderedDict()
    url = Bot_site + urllib.parse.unquote(detail_url)
    res1 = requests.get(url, headers=UA_head)
    res1.encoding = Bot_site_encoding
    text = res1.text
    text2 = re.search(r'<ul.class="stui-content__playlist.clearfix".+?</ul>', text) # 缩小搜索范围
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
        print('maliao_debug:本视频暂无播放地址')
        Plugin_dialog.notification(heading=Plugin_name, message='本视频暂无播放地址', time=3000)
        play_list.clear()
    return play_list

# 【获取电影播放绝对地址】
def site_load_vod_play(play_url):
    url = Bot_site + urllib.parse.unquote(play_url)
    res = requests.get(url, headers=UA_head)
    res.encoding = Bot_site_encoding
    code = res.text
    GZ_videos = re.compile(r'vod_name.?=.?\'(.+?)\'.+vod_part.?=.?\'(.+?)\'.+"link_pre":.+?,"url":"(.+)","url_next"')
    bofang = GZ_videos.findall(code)
    if len(bofang) > 0:
        for b in bofang:
            # 字符传入kodi需要做unicode转码
            play_names = b[0] + '[' + b[1] + ']' + u'[COLOR yellow]【开始播放】[/COLOR]'
            play_m3u8 = b[2].replace('\/', '/') # \/ 替换为 /
            # KODI代码嵌入开始
            listitem = xbmcgui.ListItem(play_names)
            xbmcplugin.addDirectoryItem(Plugin_handle, play_m3u8, listitem, False)
        xbmcplugin.endOfDirectory(Plugin_handle) # kodi菜单目录结束
    else:
        print('maliao_debug:找不到播放地址')
        Plugin_dialog.notification(heading=Plugin_name, message='抱歉，暂时无法获取播放地址', time=3000)

# 搜索视频信息
def site_load_search(keyword):
    so_url = Bot_site + '/vodsearch/-------------.html?wd=' + keyword + '&submit='
    zy = requests.get(url=so_url,headers=UA_head) # get or post
    code = zy.text
    gz = re.compile(r'<li.+?class="thumb">.+?href="(.+?)".title="(.+?)".data-original="(.+?)".+?</li>')
    sos = gz.findall(code)
    if len(sos) > 0:
        for so in sos:
            # 构造带问号的插件网址，以便于后面kodi识别：?kodi_video=/hanju/174606.html
            v_url = '?kodi_detail=' + so[0]
            v_title = so[1]
            if 'http' in so[2]:
                v_images = so[2]
            else:
                v_images = Bot_site + so[2]
            # 屏蔽少儿不宜内容
            if Bot_site_18 == True:
                if v_title in Bot_site_blackwords:
                    continue
                else:
                    listitem = xbmcgui.ListItem(v_title)
                    listitem.setArt({'thumb': v_images}) # 此设置方法适用于kodi 19+
                    xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + v_url, listitem, True)
            else:
                listitem = xbmcgui.ListItem(v_title)
                listitem.setArt({'thumb': v_images}) # 此设置方法适用于kodi 19+
                xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + v_url, listitem, True)
        xbmcplugin.endOfDirectory(Plugin_handle) # kodi 文件夹结束
    else:
        print('maliao_debug:搜索不到内容')
        Plugin_dialog.notification(heading=Plugin_name, message='抱歉，暂时无法找到此内容', time=3000)

# 当前选择>首页，为用户【建立主菜单】
if Plugin_URL_parm == '':
    # 先做一个搜索按钮
    listitem=xbmcgui.ListItem('[COLOR yellow]搜索[/COLOR]')
    xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL+'?kodi_search=yes', listitem, True)
    xbmcplugin.endOfDirectory(Plugin_handle) # kodi 文件目录布局结束，必须结束，否则程序不会停止布局
    # 载入分类列表，并生成栏目菜单
    site_make_menu()

# 当前选择>搜索按钮位置
if '?kodi_search=yes' in Plugin_URL_parm:
    keyboard = xbmc.Keyboard('', '请输入影片关键词')
    xbmc.sleep(1500)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()
        if len(keyword) < 1:
            msgbox = Plugin_dialog.ok(Plugin_name, '您必须输入关键词才可以搜索相关内容')
        else:
            site_load_search(keyword)
        
# 当前选择>栏目列表位置
if '?kodi_type=' in Plugin_URL_parm:
    # ?kodi_type=/type_1.html，由上层构造的kodi url地址，_通过wh_url来辨认
    type_url = Plugin_URL_parm.split("kodi_type=")[1]
    if type_url !=  "":
        site_load_type(type_url)
    else:
        print('maliao_debug:无法访问栏目')
        Plugin_dialog.notification(heading=Plugin_name, message='此栏目无效，无法访问此栏目', time=3000)

# 当前选择>为视频详情
if '?kodi_detail=' in Plugin_URL_parm:
    detail_url = Plugin_URL_parm.split("kodi_detail=")[1]
    if detail_url != "":
        this_list = site_load_vod_detail(detail_url)
        # print('maliao_debug:',this_list)
        # 生成播放地址列表
        for t_play, t_url in this_list.items():
            listitem = xbmcgui.ListItem(t_play)
            xbmcplugin.addDirectoryItem(Plugin_handle, Plugin_URL + t_url, listitem, True)
        xbmcplugin.endOfDirectory(Plugin_handle) # kodi 文件目录布局结束，必须结束，否则程序不会停止布局
    else:
        print('maliao_debug:无法访问视频信息')
        Plugin_dialog.notification(heading=Plugin_name, message='此视频无效，无法访问此视频', time=3000)

# 当前选择>视频播放地址
if '?kodi_play=' in Plugin_URL_parm:
    play_url = Plugin_URL_parm.split("kodi_play=")[1]
    if play_url != "":
        site_load_vod_play(play_url)
    else:
        print('maliao_debug:无法获取播放内容')
        Plugin_dialog.notification(heading=Plugin_name, message='抱歉，暂时无法获取播放内容', time=3000)

# 目录构建完了，退出菜单布局
# xbmcplugin.endOfDirectory(Plugin_handle)