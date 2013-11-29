# Copyright (c) 2010 by John Anderson <sontek@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# History
# 2011-10-24, Dmitry Geurkov <dmitry_627@mail.ru>
#   version 0.4.1: added: option "ignore_list" for a blacklist of shorten urls.
# 2011-01-17, nils_2 <weechatter@arcor.de>
#   version 0.4: URI will be shorten in /query, too.
#              : added: option "short_own".
# 2010-11-08, John Anderson <sontek@gmail.com>:
#   version 0.3: Get python 2.x binary for hook_process (fixes problem
#                when python 3.x is default python version, requires
#                WeeChat >= 0.3.4)

import re
import weechat
from urllib import urlencode
from urllib2 import urlopen

SCRIPT_NAME    = "scl_shortenurl"
SCRIPT_AUTHOR  = "Steeve Chailloux <steevechailloux@gmail.com>"
SCRIPT_VERSION = "0.4.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Shorten long incoming and outgoing URLs"

ISGD = 'http://is.gd/api.php?%s'
TINYURL = 'http://tinyurl.com/api-create.php?%s'

# script options
# shortener options:
#  - isgd
#  - tinyurl

settings = {
    "color": "red",
    "urllength": "30",
    "shortener": "isgd",
    "ignore_list": "http://is.gd,http://tinyurl.com",
}

octet = r'(?:2(?:[0-4]\d|5[0-5])|1\d\d|\d{1,2})'
ipAddr = r'%s(?:\.%s){3}' % (octet, octet)
# Base domain regex off RFC 1034 and 1738
label = r'[0-9a-z][-0-9a-z]*[0-9a-z]?'
domain = r'%s(?:\.%s)*\.[a-z][-0-9a-z]*[a-z]?' % (label, label)
urlRe = re.compile(r'(\w+://(?:%s|%s)(?::\d+)?(?:/[^\])>\s]*)?)' % (domain, ipAddr), re.I)


if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE,
                    SCRIPT_DESC, "", ""):

    for option, default_value in settings.iteritems():
        if weechat.config_get_plugin(option) == "":
            weechat.config_set_plugin(option, default_value)

    weechat.hook_modifier("weechat_print", "inside_hook", "")
    weechat.hook_modifier("irc_out_privmsg", "outside_hook", "")

def inside_hook(data, modifier, modifier_data, string):
    return short_all_url(string, True)

def outside_hook(data, modifier, modifier_data, string):
    return short_all_url(string, False)

def short_all_url(string, use_color):
    new_message = string
    color = weechat.color(weechat.config_get_plugin("color"))
    reset = weechat.color('reset')
    for url in urlRe.findall(string):
        if len(url) > int(weechat.config_get_plugin('urllength')) and not ignore_url(url):
            short_url = tiny_url(url)
            if use_color:
                new_message = new_message.replace(url, '%s%s%s' % (color, short_url, reset))
            else:
                new_message = new_message.replace(url, short_url)
        elif use_color:
            new_message = new_message.replace(url, '%s%s%s' % (color, url, reset))

    return new_message

def tiny_url(url):
    shortener = weechat.config_get_plugin('shortener')
    if shortener == 'isgd':
        url = ISGD % urlencode({'longurl':url})
    if shortener == 'tinyurl':
        url = TINYURL % urlencode({'url':url})
    try:
        return urlopen(url).read()
    except:
        return  url

def ignore_url(url):
  ignorelist = weechat.config_get_plugin('ignore_list').split(',')

  for ignore in ignorelist:
      if len(ignore) > 0 and ignore in url:
          return True

  return False
