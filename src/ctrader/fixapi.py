import time
import random
import re
import os
import tkinter as tk # should be included in your python installation 
import asyncio
import socket



#***********************************************************************

# Hello Adrian

# below is the code i have written for you that shows you how to connect to fix using port 5201
# It also shows you the heart being sent every second to the server
# You are able to buy and close all positions with the gui buttons when you run application - currency set is GBPJPY
# please note you will probably need to install tkinter using pip and you can run the application
# if you have any question please let me know
# kind regards - Hishal

#***********************************************************************


# region CHECK INTERNET CONNECTION
def tcp_ping(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2) # set timeout to 2 seconds
        sock.connect((host, port))
        sock.close()
        return True
    except:
        return False
# endregion

# region CHECKSUM CALCULATION - calculates the checksum used for validating fix messages
def checksum(message):
    sum = 0
    message_array = bytes(message, 'UTF-8')
    for i in message_array:
        sum += i
    return str((sum % 256)).zfill(3)
# endregion

#region RANDOM STRING GENERATOR - creates a random string for the sendersubid 
def random_string():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_s = ''
    for i in range(9):
        random_index = random.randint(0, len(characters)-1)
        random_s += characters[random_index]
    return random_s
#endregion

# region INITIAL GLOBAL VARIABLE DECLARATION - used for the graphical user interface
icmarkets = None
ic_bid_label = None
ic_ask_label = None
ic_price_check_state = None
ic_trade_check_state = None
ic_increment_entry = None
ic_total_lots = None
ic_opened_positions = None
ic_opened_orders = None
ic_price_check_state = None
ic_trade_check_state = None
ic_increment_entry = None
ic_total_lots = None
ic_opened_positions = None
ic_opened_orders = None
# endregion

#broker class to create instances of broker like icmarkets or broker1, 2, 3, etc
class Broker:

    def __init__(self, broker, hostname, price_reader, price_writer, trade_reader, trade_writer, sendercompid, price_sendersubid, trade_sendersubid, price_msgseqnum, trade_msgseqnum, bid, ask,
                 username, password, bid_label, ask_label, price_chk, trade_chk, positions, increment_entry, total_lots, opened_positions):
        self.broker = broker
        self.hostname = hostname
        self.price_reader = price_reader
        self.price_writer = price_writer
        self.trade_reader = trade_reader
        self.trade_writer = trade_writer
        self.sendercompid = sendercompid
        self.price_msgseqnum = price_msgseqnum
        self.trade_msgseqnum = trade_msgseqnum
        self.price_sendersubid = price_sendersubid
        self.trade_sendersubid = trade_sendersubid
        self.bid = bid
        self.ask = ask
        self.username = username
        self.password = password
        self.bid_label = bid_label
        self.ask_label = ask_label
        self.price_chk = price_chk
        self.trade_chk = trade_chk
        self.positions = positions
        self.increment_entry = increment_entry
        self.total_lots = total_lots
        self.opened_positions = opened_positions

    # region FIX MESSAGE CONSTRUCTORS

    def price_login(self):
        bl = f'35=A|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|98=0|108=1|141=Y|553={self.username}|554={self.password}|'
        self.price_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def trade_login(self): 
        bl = f'35=A|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|98=0|108=1|141=Y|553={self.username}|554={self.password}|'
        self.trade_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def price_heartbeat(self): 
        bl = f'35=0|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|'
        self.price_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def trade_heartbeat(self): 
        bl = f'35=0|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|'
        self.trade_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def market_data_request(self): 
        bl = f'35=V|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|262=GBPJPY|263=1|264=1|265=1|146=1|55=7|267=2|269=0|269=1|'
        self.price_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def request_positions(self): 
        bl = f'35=AN|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|710={self.trade_msgseqnum}|'
        self.trade_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def buy_market_order(self): 
        bl = f'35=D|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|11={self.trade_msgseqnum}|55=2|54=1|60={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|38={self.increment_entry.get()}|40=1|'
        self.trade_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'
    
    def sell_market_order(self, posid):
        bl = f'35=D|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|11={self.trade_msgseqnum}|55=2|54=2|60={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|38={self.increment_entry.get()}|40=1|721={posid}|'
        self.trade_msgseqnum += 1
        message = f'8=FIX.4.4|9={str(len(bl))}|{bl}'.replace('|', '\u0001')
        return message + f'10={checksum(message)}\u0001'

    # endregion

    # region LOGIN TO PRICE AND TRADE STREAM
    async def price_login_main(self): #PRICE STREAM
        try:
            print(f'Loggin into {self.broker} PRICE stream...')
            self.price_reader, self.price_writer = await asyncio.open_connection(self.hostname, 5201)
            self.price_sendersubid = random_string()
            self.price_writer.write(bytes(self.price_login() + self.market_data_request(), 'UTF-8'))
            asyncio.create_task(self.send_price_heartbeat())
            await self.read_price_data()
        except Exception as e:
            await asyncio.sleep(1)
            print(f"there was a connection refused error! {e}")

    async def trade_login_main(self): #TRADE STREAM
        try:
            print(f'Loggin into {self.broker} TRADE stream...')
            self.trade_reader, self.trade_writer = await asyncio.open_connection(self.hostname, 5202)
            self.trade_sendersubid = random_string()
            self.trade_writer.write(bytes(self.trade_login(), 'UTF-8'))
            asyncio.create_task(self.send_trade_heartbeat())
            await self.read_trade_data()
        except Exception as e:
            await asyncio.sleep(1)
            print(f"TRADE connection refused login error! {e}")
    # endregion

    # region HEARTBEAT METHODS FOR PRICE AND TRADE STREAMS
    async def send_price_heartbeat(self): #PRICE HEARTBEAT USED TO SEND HEARTBEAT TO SERVER EVERY 1 SECOND
        while True:
            try:
                self.price_writer.write(bytes(self.price_heartbeat(), 'UTF-8'))
            except Exception as e:
                print(f'There was a PRICE heartbeat error... {e}')
                break
            await asyncio.sleep(1) # SET TIME HERE TO THE TIME SET IN THE LOGIN MESSAGE

    async def send_trade_heartbeat(self): #SAME AS ABOVE BUT FOR TRADE HEARTBEAT
        while True:
            try:
                self.trade_writer.write(bytes(self.trade_heartbeat() + self.request_positions(), 'UTF-8'))
            except:
                print(f'There was a TRADE heartbeat error...')
                break
            await asyncio.sleep(1)
    # endregion

    # region BUTTON CLICK METHODS
    async def buy(self): # THIS IS THE BUY BUTTON ACTION THAT EXECUTES THE BUY ORDERS
        bo = ''
        for i in range(int(self.total_lots.get())):
            bo += self.buy_market_order()
        try:
            self.trade_writer.write(bytes(bo, "UTF-8"))
        except Exception as e:
            print(f"{self.broker} buying not working! {e}")

    async def closeall(self): # CLOSES ALL POSITIONS RELATING TO SYMBOL
        ca = ''
        for p in self.positions:
            ca += self.sell_market_order(p)
        try:
            self.trade_writer.write(bytes(ca, "UTF-8"))
        except:
            print(f"Unable to close all positions {self.broker}")
        self.positions.clear()
    # endregion

    # region READ PRICE STREAM
    async def read_price_data(self): # reads data asynchronously from the price stream
        while True:
            try:
                header = await self.price_reader.read(16)
                header = header.decode().replace('\u0001', '|')
                if index := re.search('9=(\\d+)', header):
                    index = int(index.group(1))
                    ti = index - 1 if index < 100 else index
                    second = await self.price_reader.read(ti + 7) 
                    full_message = header + second.decode().replace('\u0001', '|') 
                    if '35=W' in full_message:
                        prices = re.findall('270=([^|]*)', full_message)
                        self.bid = self.bid_label["text"] = prices[0] 
                        self.ask = self.ask_label["text"] = prices[1] 
                    print(full_message)
            except Exception as e:
                print(f'PRICE Unable to read from server for {self.broker} {e} {self.price_msgseqnum}')
                if tcp_ping('www.google.com', 80):
                    asyncio.create_task(self.price_login_main())
                    break
            await asyncio.sleep(0.001)
    # endregion

    # region READ TRADE STREAM
    async def read_trade_data(self): # reads data asynchronously from the trade stream 
        while True:
            try:
                header = await self.trade_reader.read(16)
                header = header.decode().replace('\u0001', '|')
                if index := re.search('9=(\\d+)', header):
                    index = int(index.group(1))
                    ti = index - 1 if index < 100 else index
                    second = await self.trade_reader.read(ti + 7)
                    full_message = header + second.decode().replace('\u0001', '|')
                    if '704=' in full_message: 
                        self.increment_entry.delete(0, 'end')
                        self.increment_entry.insert(0, str(re.search("704=(\d+)", full_message).group(1)))  
                    if '35=AP' in full_message: 
                        if match := re.search('721=(\\d+)', full_message):
                            pid = match.group(1)
                            self.positions.append(pid) if pid not in self.positions else None
                            if match2 := re.search('727=(\\d+)', full_message):
                                self.opened_positions["text"] = str(match2.group(1)) + "  Positions"
                        else:
                            self.opened_positions["text"] = "0  Positions"
                    #if '35=AP' not in full_message:
                    print(full_message)
            except:
                print(f'TRADE Unable to read from server for {self.broker}')
                if tcp_ping('www.google.com', 80):
                    asyncio.create_task(self.trade_login_main())
                    break
            await asyncio.sleep(0.001)
    # endregion

# App class for main gui event loop
class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show()


# region WINDOWS TKINTER GRAPHICAL USER INTERFACE
class Window(tk.Tk):

    def __init__(self, loop):
        global ic_bid_label, ic_ask_label, log_box, ic_price_check_state, ic_trade_check_state, ic_increment_entry, ic_total_lots, ic_opened_positions

        self.loop = loop
        self.root = tk.Tk()
        root_width = 500 # sets the width of the window
        root_height = 250 #sets the height of the window
        self.root.configure()
        self.root.geometry(f"{root_width}x{root_height}")
        self.root.title("Demo FIX API Application - 2023") #title of gui window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # close the application when close button clicked

        # creating the gui layout and content sections of the gui
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky=tk.N, padx=(20, 0), pady=10, rowspan=10)
        menu_title = tk.Label(left_frame, text="Trading Menu", font=("Ariel", 14, "bold"))
        menu_title.grid(row=0, column=0)
        content = tk.Frame(self.root, width=1180)
        content.grid(row=0, column=1, padx=15, pady=15, columnspan=10)
        ic_frame = tk.LabelFrame(content, text="IC Markets Broker", font=("Ariel", "10", "bold"))
        ic_frame.grid(row=0, column=0, sticky=tk.W, padx=10)

        # region LEFT MENU BUTTONS
        login_btn = tk.Button(left_frame, text="Login", width=11, font=("Ariel", 11, "bold"), command=lambda: self.loop.create_task(self.login()))
        login_btn.grid(row=1, column=0, pady=(15, 8))
        buy_btn = tk.Button(left_frame, text="Buy Algo", font=("Ariel", 11, "bold"), width=11, command=lambda: self.loop.create_task(self.buy()))
        buy_btn.grid(row=2, column=0, pady=8)
        close_btn = tk.Button(left_frame, text="Close All", width=11, font=("Ariel", 11, "bold"), command=lambda: self.loop.create_task(self.closeall()))
        close_btn.grid(row=5, column=0, pady=8)
        # endregion

        # region IC MARKETS PANEL
        ic_bid_label = tk.Label(ic_frame, font=("Harlow Solid Italic", "22"), width=5)
        ic_bid_label.grid(row=1, column=0, padx=10)
        ic_ask_label = tk.Label(ic_frame, font=("Harlow Solid Italic", "22"), width=5)
        ic_ask_label.grid(row=1, column=1, padx=10)
        ic_increment_label = tk.Label(ic_frame, text="Increment Size: ", font=("Ariel", "9", "bold"))
        ic_increment_label.grid(row=2, column=0, sticky=tk.W, padx=(10, 0), pady=2)
        ic_increment_entry = tk.Entry(ic_frame, font=("Ariel", "9", "bold"), width=10, borderwidth=0)
        ic_increment_entry.grid(row=2, column=1)
        ic_increment_entry.insert(0, "1000")
        ic_total_label = tk.Label(ic_frame, text="Total Lots: ", font=("Ariel", "9", "bold"))
        ic_total_label.grid(row=3, column=0, sticky=tk.W, padx=(10, 0), pady=2)
        ic_total_lots = tk.Entry(ic_frame, font=("Ariel", "9", "bold"), width=10, borderwidth=0)
        ic_total_lots.grid(row=3, column=1)
        ic_total_lots.insert(0, "8")
        ic_opened_positions = tk.Label(ic_frame, text="0  Positions", font=("LCDMono2", "12", "bold"))
        ic_opened_positions.grid(row=4, column=0, sticky=tk.W, padx=(10, 0), pady=2)
        # endregion

    async def login(self):
        global icmarkets, ic_bid_label, ic_ask_label, ic_price_check_state, ic_trade_check_state, ic_increment_entry, ic_total_lots, ic_opened_positions
        
        #create an ic market instance of broker class and login to the 2 streams ICmarkets login credentials
        icmarkets = Broker("icmarkets", "h35.p.ctrader.com", None, None, None, None, "demo.icmarkets.8739125", None, None, 1, 1, None, None, "8739125", "ghjd685j23", ic_bid_label, ic_ask_label, ic_price_check_state,
                        ic_trade_check_state, [], ic_increment_entry, ic_total_lots, ic_opened_positions)
        
        asyncio.create_task(icmarkets.price_login_main()) # login to the ic markets price stream
        asyncio.create_task(icmarkets.trade_login_main()) # login to the ic markets trade stream
        await asyncio.sleep(0)

    def on_closing(self): # destroy window and related gui elements when window is closed
        self.root.destroy()
        os._exit(0)

    async def show(self): # show window when created in the event loop
        while True:
            self.root.update()
            await asyncio.sleep(0.01)

    async def buy(self): # function to buy async when buy button clicked
        global icmarkets
        asyncio.create_task(icmarkets.buy())

    async def closeall(self): # function to close all positions when close all button is clicked
        global icmarkets
        asyncio.create_task(icmarkets.closeall())
# endregion

# runs the application
asyncio.run(App().exec())

