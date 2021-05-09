import win32api
import win32gui
import win32con
import win32clipboard
import win32process

import ctypes
import time
import math

from const import VK_CODE, BALANCE_CONTROL_ID_GROUP

sleep_time = 0.2
refresh_sleep_time = 0.5
retry_time = 10

window_title = u'网上股票交易系统5.0'

def get_clipboard_data():
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()
    return data

def hot_key(keys):
    for key in keys:
        win32api.keybd_event(VK_CODE[key], 0, 0, 0)
    for key in reversed(keys):
        win32api.keybd_event(VK_CODE[key], 0, win32con.KEYEVENTF_KEYUP, 0)

def set_text(hwnd, string):
    win32gui.SetForegroundWindow(hwnd)
    win32api.SendMessage(hwnd, win32con.EM_SETSEL, 0, -1)
    win32api.keybd_event(VK_CODE['backspace'], 0, 0, 0)
    win32api.keybd_event(VK_CODE['backspace'], 0, win32con.KEYEVENTF_KEYUP, 0)
    for char in string:
        win32api.keybd_event(VK_CODE[char], 0, 0, 0)
        win32api.keybd_event(VK_CODE[char], 0, win32con.KEYEVENTF_KEYUP, 0)

def get_text(hwnd):
    length = ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXTLENGTH)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXT, length, ctypes.byref(buf))
    return buf.value

def parse_table(text):
    lines = text.split('\t\r\n')
    keys = lines[0].split('\t')
    result = []
    for i in range(1, len(lines)):
        info = {}
        items = lines[i].split('\t')
        for j in range(len(keys)):
            info[keys[j]] = items[j]
        result.append(info)
    return result


class ThsAuto:

    def __init__(self):
        self.hwnd_main = None

    def bind_client(self):
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd > 0:
            win32gui.SetForegroundWindow(hwnd)
            self.hwnd_main = hwnd

    def kill_client(self):
        self.hwnd_main = None
        retry = 5
        while(retry > 0):
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                time.sleep(1)
                break
            else:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(sleep_time)
                hot_key(['alt', 'F4'])
                time.sleep(1)
                retry -= 1
                

    def get_tree_hwnd(self):
        hwnd = self.hwnd_main
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxMDIFrame42s', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxWnd42s', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'Afx:400000:0', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxWnd42s', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'SysTreeView32', None)
        return hwnd

    def get_right_hwnd(self):
        hwnd = self.hwnd_main
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxMDIFrame42s', None)
        hwnd = win32gui.GetDlgItem(hwnd, 0xE901)
        return hwnd

    def get_left_bottom_tabs(self):
        hwnd = self.hwnd_main
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxMDIFrame42s', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'AfxWnd42s', None)
        hwnd = win32gui.FindWindowEx(hwnd, None, 'CCustomTabCtrl', None)
        return hwnd

    def get_balance(self):
        self.switch_to_normal()
        hot_key(['F4'])
        self.refresh()
        hwnd = self.get_right_hwnd()
        data = {}
        for key, cid in BALANCE_CONTROL_ID_GROUP.items():
            ctrl = win32gui.GetDlgItem(hwnd, cid)
            if ctrl > 0 and win32gui.IsWindowVisible(ctrl):
                data[key] = get_text(ctrl)
        return {
            'code': 0, 'status': 'succeed',
            'data': data,
        }
        
    def get_position(self):
        self.switch_to_normal()
        hot_key(['F1'])
        hot_key(['F6'])
        self.refresh()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x417)

        # self.right_click_menu(ctrl, -50, -50, idx=5)
        win32gui.SetForegroundWindow(ctrl)
        hot_key(['ctrl', 'c'])

        data = None
        retry = 0
        while not data and retry < retry_time:
            retry += 1
            time.sleep(sleep_time)
            data = get_clipboard_data()
        if data:
            return {
                'code': 0, 'status': 'succeed',
                'data': parse_table(data),
            }
        return {'code': 1, 'status': 'failed'}

    def get_active_orders(self):
        self.switch_to_normal()
        hot_key(['F1'])
        hot_key(['F8'])
        time.sleep(sleep_time)
        self.refresh()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x417)

        # self.right_click_menu(ctrl, -50, -50, idx=3)
        win32gui.SetForegroundWindow(ctrl)
        hot_key(['ctrl', 'c'])
        
        data = None
        retry = 0
        while not data and retry < retry_time:
            retry += 1
            time.sleep(sleep_time)
            data = get_clipboard_data()
        if data:
            return {
                'code': 0, 'status': 'succeed',
                'data': parse_table(data),
            }
        return {'code': 1, 'status': 'failed'}
        
    def get_filled_orders(self):
        self.switch_to_normal()
        hot_key(['F2'])
        hot_key(['F7'])
        time.sleep(sleep_time)
        self.refresh()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x417)

        # self.right_click_menu(ctrl, -50, -50, idx=3)
        win32gui.SetForegroundWindow(ctrl)
        hot_key(['ctrl', 'c'])

        data = None
        retry = 0
        while not data and retry < retry_time:
            retry += 1
            time.sleep(sleep_time)
            data = get_clipboard_data()
        if data:
            return {
                'code': 0, 'status': 'succeed',
                'data': parse_table(data),
            }
        return {'code': 1, 'status': 'failed'}

    def sell(self, stock_no, amount, price):
        self.switch_to_normal()
        hot_key(['F2'])
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x408)
        set_text(ctrl, stock_no)
        time.sleep(sleep_time)
        if price is not None:
            time.sleep(sleep_time)
            price = '%.3f' % price
            ctrl = win32gui.GetDlgItem(hwnd, 0x409)
            set_text(ctrl, price)
            time.sleep(sleep_time)
        ctrl = win32gui.GetDlgItem(hwnd, 0x40A)
        set_text(ctrl, str(amount))
        time.sleep(sleep_time)
        hot_key(['enter'])
        result = None
        retry = 0
        while retry < retry_time:
            time.sleep(sleep_time)
            result = self.get_result()
            if result:
                hot_key(['enter'])
                return result
            hot_key(['y'])
            retry += 1
        return {
            'code': 2,
            'status': 'unknown',
            'msg': '获取结果失败,请自行确认订单状态',
        }

    def buy(self, stock_no, amount, price):
        self.switch_to_normal()
        hot_key(['F1'])
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x408)
        set_text(ctrl, stock_no)
        time.sleep(sleep_time)
        if price is not None:
            time.sleep(sleep_time)
            price = '%.3f' % price
            ctrl = win32gui.GetDlgItem(hwnd, 0x409)
            set_text(ctrl, price)
            time.sleep(sleep_time)
        ctrl = win32gui.GetDlgItem(hwnd, 0x40A)
        set_text(ctrl, str(amount))
        time.sleep(sleep_time)
        hot_key(['enter'])
        result = None
        retry = 0
        while retry < retry_time:
            time.sleep(sleep_time)
            result = self.get_result()
            if result:
                hot_key(['enter'])
                return result
            hot_key(['y'])
            retry += 1
        return {
            'code': 2,
            'status': 'unknown',
            'msg': '获取结果失败,请自行确认订单状态',
        }

    def sell_kc(self, stock_no, amount, price):
        self.switch_to_kechuang()
        self.click_kc_sell()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x408)
        set_text(ctrl, stock_no)
        time.sleep(sleep_time)
        if price is not None:
            time.sleep(sleep_time)
            price = '%.3f' % price
            ctrl = win32gui.GetDlgItem(hwnd, 0x409)
            set_text(ctrl, price)
            time.sleep(sleep_time)
        ctrl = win32gui.GetDlgItem(hwnd, 0x40A)
        set_text(ctrl, str(amount))
        time.sleep(sleep_time)
        hot_key(['enter'])
        result = None
        retry = 0
        while retry < retry_time:
            time.sleep(sleep_time)
            result = self.get_result()
            if result:
                hot_key(['enter'])
                return result
            hot_key(['y'])
            retry += 1
        return {
            'code': 2,
            'status': 'unknown',
            'msg': '获取结果失败,请自行确认订单状态',
        }

    def buy_kc(self, stock_no, amount, price):
        self.switch_to_kechuang()
        self.click_kc_buy()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x408)
        set_text(ctrl, stock_no)
        time.sleep(sleep_time)
        if price is not None:
            time.sleep(sleep_time)
            price = '%.3f' % price
            ctrl = win32gui.GetDlgItem(hwnd, 0x409)
            set_text(ctrl, price)
            time.sleep(sleep_time)
        ctrl = win32gui.GetDlgItem(hwnd, 0x40A)
        set_text(ctrl, str(amount))
        time.sleep(sleep_time)
        hot_key(['enter'])
        result = None
        retry = 0
        while retry < retry_time:
            time.sleep(sleep_time)
            result = self.get_result()
            if result:
                hot_key(['enter'])
                return result
            hot_key(['y'])
            retry += 1
        return {
            'code': 2,
            'status': 'unknown',
            'msg': '获取结果失败,请自行确认订单状态',
        }

    def cancel(self, entrust_no):
        self.switch_to_normal()
        hot_key(['F3'])
        self.refresh()
        hwnd = self.get_right_hwnd()
        ctrl = win32gui.GetDlgItem(hwnd, 0x417)
        
        # self.right_click_menu(ctrl, -50, -50, idx=3)
        win32gui.SetForegroundWindow(ctrl)
        hot_key(['ctrl', 'c'])

        data = None
        retry = 0
        while not data and retry < retry_time:
            retry += 1
            time.sleep(sleep_time)
            data = get_clipboard_data()
        if data:
            entrusts = parse_table(data)
            find = None
            for i, entrust in enumerate(entrusts):
                if str(entrust['合同编号']) == str(entrust_no):
                    find = i
                    break
            if find is None:
                return {'code': 1, 'status': 'failed', 'msg': u'没找到指定订单'}
            left, top, right, bottom = win32gui.GetWindowRect(ctrl)
            x = 50 + left
            y = 30 + 16 * find + top
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(sleep_time)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(sleep_time)
            hot_key(['enter'])
            return {'code': 0, 'status': 'succeed'}
        return {'code': 1, 'status': 'failed'}

    def get_result(self, cid=0x3EC):
        tid, pid = win32process.GetWindowThreadProcessId(self.hwnd_main)
        def enum_children(hwnd, results):
            try:
                if (win32gui.IsWindowVisible(hwnd) and
                        win32gui.IsWindowEnabled(hwnd)):
                    win32gui.EnumChildWindows(hwnd, handler, results)
            except Exception:
                return

        def handler(hwnd, results):
            if (win32api.GetWindowLong(hwnd, win32con.GWL_ID) == cid and 
                    win32gui.GetClassName(hwnd) == 'Static'):
                results.append(hwnd)
                return False
            enum_children(hwnd, results)
            return len(results) == 0
        popups = []
        windows = []            
        win32gui.EnumThreadWindows(tid, lambda hwnd, l: l.append(hwnd), windows)
        for hwnd in windows:
            if not handler(hwnd, popups):
                break
        if popups:
            ctrl = popups[0]
            text = get_text(ctrl)
            if u'已成功提交' in text:
                return {
                    'code': 0,
                    'status': 'succeed',
                    'msg': text,
                    'entrust_no': text.split(u'合同编号：')[1].split('。')[0],
                }
            else:
                return {
                    'code': 1,
                    'status': 'failed',
                    'msg': text,
                }

    def refresh(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd_main)
        x = 170 + left
        y = 40 + top
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(refresh_sleep_time)

    def active_mian_window(self):
        if self.hwnd_main is not None:
            ctypes.windll.user32.SwitchToThisWindow(self.hwnd_main, True)
            time.sleep(sleep_time)

    def right_click_menu(self, hwnd, x, y, idx=None, key=None):
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        x = left + x if x > 0 else right + x
        y = top + y if y > 0 else bottom + y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        time.sleep(sleep_time)
        if idx is not None:
            while (idx >= 0):
                hot_key(['down_arrow'])
                idx -= 1
            hot_key(['enter'])
        elif hot_key is not None:
            if isinstance(key, list):
                hot_key(key)
            else:
                hot_key([key])

    def switch_to_normal(self):
        tabs = self.get_left_bottom_tabs()
        left, top, right, bottom = win32gui.GetWindowRect(tabs)
        x = left + 10
        y = top + 5
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(sleep_time)

    def switch_to_kechuang(self):
        tabs = self.get_left_bottom_tabs()
        left, top, right, bottom = win32gui.GetWindowRect(tabs)
        x = left + 200
        y = top + 5
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(sleep_time)

    def click_kc_buy(self):
        tree = self.get_tree_hwnd()
        left, top, right, bottom = win32gui.GetWindowRect(tree)
        x = left + 10
        y = top + 10
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(sleep_time)

    def click_kc_sell(self):
        tree = self.get_tree_hwnd()
        left, top, right, bottom = win32gui.GetWindowRect(tree)
        x = left + 10
        y = top + 30
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(sleep_time)

    def test(self):
        pass

