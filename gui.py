from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from ctypes import windll
from config import *
from actions import load_data,send_sms
import threading

total = 0
present = 0
index = 0
limit = 0
filename= ''
phone_input = ''
message_input = ''
wait_input = ''
count_input = ''
api_input = ''
start_stop_btn = ''
hold = False
tk_title = "Esmex" # Put here your window title


def stop():
    global state
    global hold

    state['ON'] = False
    display_text['fg'] = '#E74C3C'
    display_text['text'] = 'Stopping ...'

    start_stop_btn.config(image=start_img)
    start_stop_btn.config(command=lambda:loader(target=open_popup,args={'title':'Start operation','header':'click "start" to begin','text':'(Enter phone number in this format:+1234567890)','kind':'start'}))
    hold = False

def start(widget=''):
    try:
        global phone_input
        global message_input
        global wait_input
        global count_input
        global state
        global display_text
        global index
        global limit
        global hold
        s_phone = phone_input.get()
        s_message = message_input.get(1.0,END)
        s_wait = wait_input.get()

        wait = int(s_wait) if s_wait else 5
        s_phone = str(s_phone).split(",")
        phone = s_phone[0]

        s_message = str(s_message).strip().split("===")
        message = s_message[0]

        s_count = count_input.get()
        s_count = int(s_count) if s_count else 0

        if not s_message or not s_phone:
            state['ON'] = False
            start_stop_btn.config(image=start_img)
            display_text['fg'] = '#E74C3C'
            display_text['text'] = 'Error: some inputs are empty!'
        else:
            start_stop_btn.config(image=stop_img)
            start_stop_btn.config(command=lambda:loader(target=stop,text='stoping all operations...',text_color='#E74C3C'))
            
            state['ON'] = True
            
            display_text['fg'] = '#1ABC9C'
            display_text['text'] = f'Starting operation with script {message} \n Click on power button to stop'
            
            widget.destroy()

            i,j,count,all_sent,index = 0,0,0,0,0
            limit = s_count if s_count > 0 and s_count <= 20 else 20
           
            l_count = load_data(index,limit)
            l_count = l_count[3] if l_count[0] else 0
            

            while l_count > 0 and state['ON']:
                try:
                    data = load_data(index,limit)
                    if data[0]:
                        sent = handle_sms(wait=wait,data=data[1]["data"],s_phone=phone,s_message=message,limit=limit)
                        all_sent += sent[0]
                        count += sent[0]

                        display_text['text'] = ''
                        display_text['fg'] = '#1ABC9C'
                        display_text['text'] = f'{count} messsages sent by {sent[1]}'
                                
                    else:
                        display_text['fg'] = '#E74C3C'
                        display_text['text'] = data[1]

                except Exception as error:
                    display_text['fg'] = '#E74C3C'
                    display_text['text'] = error

                l_count -= 1
                index += 1
                if state['ON']:
                    display_text['fg'] = '#1ABC9C'
                    display_text['text'] = f'sleeping for {wait} seconds'
                    time.sleep(wait)
                    
                    if s_count > 0 and count >= s_count:
                        i = i + 1 if i < len(s_message) - 1 else 0
                        j = j + 1 if j < len(s_phone) - 1 else 0
                        
                        count = 0

                        time.sleep(2)
                        message = s_message[i]
                        phone = s_phone[j]
                        display_text['fg'] = '#1ABC9C'
                        display_text['text'] = f'Switching script and phone number'

                        time.sleep(2)

                        display_text['fg'] = '#1ABC9C'
                        display_text['text'] = f'Script switched to {message} and number {phone}'

            display_text['fg'] = '#1ABC9C'
            display_text['text'] = f'Sent {all_sent} total messages'

            start_stop_btn.config(image=start_img)
            start_stop_btn.config(command=lambda:loader(target=open_popup,args={'title':'Start operation','header':'click "start" to begin','text':'(Enter phone number in this format:+1234567890)','kind':'start'}))
    except Exception as error:
        display_text['fg'] = '#E74C3C'
        display_text['text'] = error

        start_stop_btn.config(image=start_img)
        start_stop_btn.config(command=lambda:loader(target=open_popup,args={'title':'Start operation','header':'click "start" to begin','text':'(Enter phone number in this format:+1234567890)','kind':'start'}))
    state['ON'] = False
    hold = False

def handle_sms(wait=0,data={},s_phone='',s_message='',limit=20):
    global display_text
    sent = 0
    try:
        kwargs = [{
                'local_number':s_phone,
                'remote_number':contact['phones'][0]['phone'],
                'contact_id': contact['id'],
                'lead_id':contact['lead_id'],
                'proxies':random.choice(proxies) if len(proxies) > 0 else {},
                'message':s_message,
                'wait':wait,
                'api_key':api_key
            }for contact in data if len(contact['phones']) > 0]

        with ThreadPoolExecutor(max_workers=limit) as executor:
            futures = []
            for kwargs in kwargs:
                future = executor.submit(send_sms, **kwargs)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                display_text['text'] = ''
                if result[0]:
                    display_text['fg'] = '#1ABC9C'
                    display_text['text'] = f'Message sent to {result[1]} by {s_phone}'
                    sent += 1
                else:
                    display_text['fg'] = '#E74C3C'
                    display_text['text'] = f'{result[1]} on {s_phone}'
            
            return sent,s_phone

                    
    except Exception as error:
        display_text['fg'] = '#E74C3C'
        display_text['text'] = f'{error} on {s_phone}'
        return sent,s_phone

def write_api(widget=''):
    global hold
    global display_text
    global api_key
    global api
    try:
        new_api = api_input.get()
        if new_api:
            with open(env_path,'w') as env:
               env.write(f'APIKEY={str(new_api).strip()}')
            # try:
            #     subprocess.call(['setx', 'APIKEY', str(new_api).strip()])
            # except:
            #     with open(str(Path.home()) + '/.profile', 'a') as f:
            #         f.write(f'export APIKEY={str(new_api).strip()}')
            api_key = new_api
            api = Client(api_key)

            display_text['fg'] = '#F0F0F0'
            display_text['text'] = f'api key changed to {api_key}'
        else:
            display_text['fg'] = '#E74C3C'
            display_text['text'] = 'Error: api key is empty!'
    except Exception as error:
        display_text['fg'] = '#E74C3C'
        display_text['text'] = f'Error: {error}'
    widget.destroy()
    hold = False


def open_popup(title='',header='',text='',ext='',kind=''):
    global phone_input
    global message_input
    global wait_input
    global count_input
    global api_input
    global display_text
    global state
    global hold

    if kind == 'start':
        width,height = 500,600 
        if state['ON']:state['ON'] = False
    else:width,height = 400,200

    popup = Toplevel()
    popup.iconbitmap(logo)
    popup.title(title)
    popup.geometry("{}x{}+{}+{}".format(width,height,int(popup.winfo_screenwidth()/2 - width/2), int(popup.winfo_screenheight()/2 - height/2)))

    header = Label(popup, text=header,font=('helvetica', 12))
    header.pack()

    text = Label(popup, text=text,font=('helvetica', 10),wraplength=400)
    text.pack()

    def load_file(kind):
        global filename
        global proxies
        try:
            file_path = filedialog.askopenfilename(filetypes=[('Text files', f'*.{ext}')])
            popup.destroy()

            filename = 'Selected file: {}'.format(file_path).split('/')
            filename = filename[len(filename)-1]
            with open(file_path,'r') as r_file:
                data = r_file.read()
                with open(proxy_file,'w') as w_file:
                    w_file.write(data)
                proxies = load_proxies()
            display_text['fg'] = '#F0F0F0'
            display_text['text'] = f'{kind} loaded successfully'
        except Exception as error:
            display_text['fg'] = '#E74C3C'
            display_text['text'] = f'error loading data from {filename} because: {error}'
    if kind == 'proxies':
        button = Button(popup, text=f'Load {kind}', command=lambda:load_file(kind=kind))
        button.pack(pady=10)
    elif kind == 'start':
        label = Label(popup, text="Enter sender phone number(s) seperated by comma:")
        label.place(relx=0.15,rely=0.10)
        phone_input = Entry(popup, textvariable=StringVar(), validate='key')
        phone_input.configure(validatecommand=(phone_input.register(lambda char: char.isdigit() or char in [","," ","-","+"]), '%S'))
        phone_input.place(relx=0.15,rely=0.15,relwidth=0.7,relheight=0.05)

        label = Label(popup, text="Enter message should be seperated by (===) if more than 1:")
        label.place(relx=0.15,rely=0.225)
        message_input = Text(popup)
        message_input.place(relx=0.15,rely=0.275,relwidth=0.7,relheight=0.3)

        label = Label(popup, text="Enter wait time (e.g 20 = 20 seconds, 60 = 1 minute):")
        label.place(relx=0.15,rely=0.6)
        wait_input = Entry(popup, textvariable=StringVar(), validate="key")
        wait_input.configure(validatecommand=(wait_input.register(lambda char: char.isdigit()), '%S'))
        wait_input.place(relx=0.15,rely=0.65,relwidth=0.7,relheight=0.05)

        label = Label(popup, text="Enter when you want to switch scripts and numbers (e.g 1000)")
        label.place(relx=0.15,rely=0.725)
        count_input = Entry(popup, textvariable=StringVar(), validate="key")
        count_input.configure(validatecommand=(count_input.register(lambda char: char.isdigit()), '%S'))
        count_input.place(relx=0.15,rely=0.775,relwidth=0.7,relheight=0.05)

        button = Button(popup, text=f'Start', command=lambda:loader(target=start,args={'widget':popup}))
        button.place(relx=0.35,rely=0.88,relwidth=0.25,relheight=0.06)
    
    elif kind == 'API':
        s_string = StringVar()

        label = Label(popup, text="Enter api key:")
        label.place(relx=0.125,rely=0.35)


        api_input = Entry(popup, textvariable=s_string, validate='key')
        api_input.place(relx=0.125,rely=0.45,relwidth=0.8,relheight=0.15)

        button = Button(popup, text=f'Apply', command=lambda:loader(target=write_api,args={'widget':popup}))
        button.place(relx=0.4,rely=0.65,relwidth=0.2,relheight=0.15)
    
    else:
        display_text['fg'] = '#F0F0F0'
        display_text['text'] = ''
    hold = False


def load_contacts(type="close",offset=0,limit=0,count=0):
    global data
    global display_text
    global t_items
    global p_items
    global total
    global index
    global present
    global hold

    try:
        counter = 0
        has_more = True
        data = {"data":[]}
        if type == "close":
            while counter < count or has_more:
                lead_results = api.get("contact", params={
                    "_limit": limit,
                    "_skip": offset,
                    "_fields":"id,display_name,title,status_label,phones,date_created",
                })

                has_more = lead_results["has_more"]
                data["data"] += lead_results["data"]
                offset = len(data["data"])
                counter += offset
                time.sleep(2)
            with open(leads_file,"w",encoding="utf-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=4)

        data = load_data(0,20)
        if data[0]:
            index = 0
            total = data[2]
            present = len(data[1]["data"])
            display_text["text"] = "contacts loaded successfully"
            display_text["fg"] = "#F0F0F0"

            t_items["text"] = f"total: {total}"
            p_items["text"] = f"{present}/{total}"

            display_data(data)
        else:
            display_text["fg"] = "#E74C3C"
            display_text["text"] = f"{data[1]}"

    except Exception as error:
        display_text["fg"] = '#E74C3C'
        display_text["text"] = f"{error}, key:{api_key}"
    hold = False

def loader(target=any,text="Loading ...",text_color="#F0F0F0",args={}):
    global hold
    if not hold or target == stop:
        hold = True
        t = threading.Thread(target=target, kwargs=args)
        t.start()
        display_text["fg"] = f"{text_color}"
        display_text["text"] = f"{text}"

root=Tk()
root.iconbitmap(logo)
root.title(tk_title) 
root.overrideredirect(True) # turns off title bar, geometry
root.geometry("1100x600") # define the window size
root.minsize(700, 500) # define the window min-size

screen_width = root.winfo_screenwidth() # get the window screen width
screen_height = root.winfo_screenheight() # get the window screen height

# get the x and y axis
x = int((screen_width/2) - (1100/2)) 
y = int((screen_height/2) - (600/2))

root.geometry("+{}+{}".format(x, y)) # set the startup location

#root.iconbitmap("your_icon.ico") # to show your own icon 
root.minimized = False # only to know if root is minimized
root.maximized = False # only to know if root is maximized

LGRAY = '#3e4042' # button color effects in the title bar (Hex color)
DGRAY = '#363846' # window background color               (Hex color)
RGRAY = '#292a33' # title bar color                       (Hex color)

root.config(bg=DGRAY)
title_bar = Frame(root, bg=DGRAY, relief='raised', bd=0,highlightthickness=0)


def set_appwindow(mainWindow): # to display the window icon on the taskbar
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    # Magic
    hwnd = windll.user32.GetParent(mainWindow.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)
   
    mainWindow.wm_withdraw()
    mainWindow.after(10, lambda: mainWindow.wm_deiconify())
    

def minimize_me():
    root.attributes("-alpha",0) # so you can't see the window when is minimized
    root.minimized = True       


def deminimize(event):

    root.focus() 
    root.attributes("-alpha",1) # so you can see the window when is not minimized
    if root.minimized == True:
        root.minimized = False                              
        

def maximize_me():

    if root.maximized == False: # if the window was not maximized
        root.normal_size = root.geometry()
        expand_button.config(text=" 🗗 ")
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.maximized = not root.maximized 
        # now it's maximized
        
    else: # if the window was maximized
        expand_button.config(text=" 🗖 ")
        root.geometry(root.normal_size)
        root.maximized = not root.maximized
        # now it is not maximized

# put a close button on the title bar
close_button = Button(title_bar, text='  ×  ', command=root.destroy,bg=DGRAY,padx=2,pady=2,font=("calibri", 13),bd=0,fg='white',highlightthickness=0)
expand_button = Button(title_bar, text=' 🗖 ', command=maximize_me,bg=DGRAY,padx=2,pady=2,bd=0,fg='white',font=("calibri", 13),highlightthickness=0)
minimize_button = Button(title_bar, text=' 🗕 ',command=minimize_me,bg=DGRAY,padx=2,pady=2,bd=0,fg='white',font=("calibri", 13),highlightthickness=0)
title_bar_title = Label(title_bar, text=tk_title, bg=DGRAY,bd=0,fg='white',font=("helvetica", 14),highlightthickness=0)

# a frame for the main area of the window, this is where the actual app will go
window = Frame(root, bg=DGRAY,highlightthickness=0)

# pack the widgets
title_bar.pack(fill=X,padx=5,pady=5)
close_button.pack(side=RIGHT,ipadx=7,ipady=1)
expand_button.pack(side=RIGHT,ipadx=7,ipady=1)
minimize_button.pack(side=RIGHT,ipadx=7,ipady=1)
title_bar_title.pack(side=LEFT, padx=10)

def changex_on_hovering(event):
    global close_button
    close_button['bg']='red'
    
    
def returnx_to_normalstate(event):
    global close_button
    close_button['bg']=DGRAY
    

def change_size_on_hovering(event):
    global expand_button
    expand_button['bg']=LGRAY
    
    
def return_size_on_hovering(event):
    global expand_button
    expand_button['bg']=DGRAY
    

def changem_size_on_hovering(event):
    global minimize_button
    minimize_button['bg']=LGRAY
    
    
def returnm_size_on_hovering(event):
    global minimize_button
    minimize_button['bg']=DGRAY
    

def get_pos(event): # this is executed when the title bar is clicked to move the window
    if root.maximized == False:
 
        xwin = root.winfo_x()
        ywin = root.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        
        def move_window(event): # runs when window is dragged
            root.config(cursor="fleur")
            root.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')


        def release_window(event): # runs when window is released
            root.config(cursor="arrow")
            
            
        title_bar.bind('<B1-Motion>', move_window)
        title_bar.bind('<ButtonRelease-1>', release_window)
        title_bar_title.bind('<B1-Motion>', move_window)
        title_bar_title.bind('<ButtonRelease-1>', release_window)
    else:
        expand_button.config(text=" 🗖 ")
        root.maximized = not root.maximized

title_bar.bind('<Button-1>', get_pos) # so you can drag the window from the title bar
title_bar_title.bind('<Button-1>', get_pos) # so you can drag the window from the title 

# button effects in the title bar when hovering over buttons
close_button.bind('<Enter>',changex_on_hovering)
close_button.bind('<Leave>',returnx_to_normalstate)
expand_button.bind('<Enter>', change_size_on_hovering)
expand_button.bind('<Leave>', return_size_on_hovering)
minimize_button.bind('<Enter>', changem_size_on_hovering)
minimize_button.bind('<Leave>', returnm_size_on_hovering)

# resize the window width
resizex_widget = Frame(window,bg=DGRAY,cursor='sb_h_double_arrow')
resizex_widget.pack(side=RIGHT,ipadx=2,fill=Y)


def resizex(event):
    xwin = root.winfo_x()
    difference = (event.x_root - xwin) - root.winfo_width()
    
    if root.winfo_width() > 150 : # 150 is the minimum width for the window
        try:
            root.geometry(f"{ root.winfo_width() + difference }x{ root.winfo_height() }")
        except:
            pass
    else:
        if difference > 0: # so the window can't be too small (150x150)
            try:
                root.geometry(f"{ root.winfo_width() + difference }x{ root.winfo_height() }")
            except:
                pass
              
    resizex_widget.config(bg=DGRAY)

resizex_widget.bind("<B1-Motion>",resizex)

# resize the window height
resizey_widget = Frame(window,bg=DGRAY,cursor='sb_v_double_arrow')
resizey_widget.pack(side=BOTTOM,ipadx=2,fill=X)

def resizey(event):
    ywin = root.winfo_y()
    difference = (event.y_root - ywin) - root.winfo_height()

    if root.winfo_height() > 150: # 150 is the minimum height for the window
        try:
            root.geometry(f"{ root.winfo_width()  }x{ root.winfo_height() + difference}")
        except:
            pass
    else:
        if difference > 0: # so the window can't be too small (150x150)
            try:
                root.geometry(f"{ root.winfo_width()  }x{ root.winfo_height() + difference}")
            except:
                pass

    resizex_widget.config(bg=DGRAY)

resizey_widget.bind("<B1-Motion>",resizey)

# some settings
root.bind("<FocusIn>",deminimize) # to view the window by clicking on the window icon on the taskbar
root.after(10, lambda: set_appwindow(root)) # to see the icon on the task bar


#table housing
t_house = Frame(root,background=RGRAY,relief='sunken')
t_house.place(relx=0.025, rely=0.1, relwidth=0.6, relheight=0.75, anchor='nw')

# create a tableview widget
table = ttk.Treeview(t_house, columns=('column1', 'column2', 'column3'), show='headings')

#styling the table
style = ttk.Style()
style.theme_use("default")
style.configure('.',borderwidth=0)
style.configure('Treeview',background=RGRAY, fieldbackground=RGRAY,borderwidth=0,padding=0,relief = 'flat')
style.configure('Treeview.Heading',background=DGRAY, fieldbackground=DGRAY,foreground='#D0D0D0',borderwidth=0,padding=10,font=('TkDefaultFont', 12))
style.configure('Treeview.Cells',font=('TkDefaultFont', 12),foreground='#D0D0D0')

# set the column headings
table.heading('column1', text='Name' )
table.heading('column2', text='Title' )
table.heading('column3', text='Phones')

# set the column widths
table.column('column1', width=100,anchor='w')
table.column('column2', width=100,anchor='center')
table.column('column3', width=100,anchor='e')


# set the column alignments
table.heading('column1', anchor='w')
table.heading('column2', anchor='center')
table.heading('column3',  anchor='e')

table['style'] = 'Treeview'
table.pack(fill=BOTH,expand=True,padx=20,pady=20)

#making a pagination bar at the table bottom
pag_bar = Frame(root,bg=DGRAY,bd=0,highlightthickness=0)
pag_bar.place(relx=0.025, rely=0.98, relwidth=0.6, relheight=0.1, anchor='sw')

#total items (present/total)
t_items_housing = Frame(pag_bar,bg=DGRAY)
t_items_housing.place(relx=0,rely=0.1,relwidth=0.6,relheight=0.50,anchor='nw')

t_items = Label(t_items_housing,bg=DGRAY,fg='#F0F0F0',font=("helvetica", 12))
t_items.pack(side='left',padx=10)

p_items = Label(t_items_housing,bg=DGRAY,fg='#F0F0F0',font=("helvetica", 12))
p_items.pack(side='right')

#more/less (previuos/next) buttons
less_btn = Button(pag_bar,bg='#E74C3C',fg='#FFFFE0',text='Less', bd=0,highlightthickness=0,font=("helvetica", 12),command=lambda:loader(target=more_or_less,text='Loading data ...',args={'type': 'less'}))
less_btn.place(relx=0.80,rely=0.1,relwidth=0.15,relheight=0.50,anchor='ne')

more_btn = Button(pag_bar,text='More',bg='#054568',fg='#F0F0F0',bd=0,highlightthickness=0,font=("helvetica", 12),command=lambda:loader(target=more_or_less,text='Loading data ...'))
more_btn.place(relx=0.98,rely=0.1,relwidth=0.15,relheight=0.50,anchor='ne')



#control console
c_frame_housing = Frame(root,bg=RGRAY)
c_frame_housing.place(relx=0.975, rely=0.1, relwidth=0.325, relheight=0.84, anchor='ne') # console holder housing

c_frame = Frame(c_frame_housing,bg=DGRAY)
c_frame.place(relx=0.05, rely=0.04, relwidth=0.9, relheight=0.925) # console holder

#operations buttons
load_proxies_btn = Button(c_frame,bg='#054568',fg='#F0F0F0',bd=0,font=("helvetica", 13),highlightthickness=0,text='Load proxies',command=lambda:loader(target=open_popup,args={'title':'Load Proxies','header':'click to load proxies','text':'(file type must be .txt and in this format: host:port:username:password)','ext':'txt','kind':'proxies'}))
load_proxies_btn.place(relx=0.05,rely=0.02,relwidth=0.9,relheight=0.06)

change_api_key = Button(c_frame,bg='#F0F0F0',fg='#054568',bd=0,font=("helvetica", 12),highlightthickness=0,text='Change API key',command=lambda:loader(target=open_popup,text='Loading ...',args={'title':'Load Leads','header':'Replace old API key with new one','text':f'old key: {api_key}','kind':'API'}))
change_api_key.place(relx=0.05,rely=0.115,relwidth=0.45,relheight=0.06)

refresh_leads = Button(c_frame,bg='#054568',fg='#F0F0F0',bd=0,font=("helvetica", 12),highlightthickness=0,text='Load from close',command=lambda:loader(target=load_contacts,text='Downloading all contacts from close.com, please wait ...',args={'offset': 0,'limit':100}))
refresh_leads.place(relx=0.55,rely=0.115,relwidth=0.4,relheight=0.06)

#console output
console = Frame(c_frame,bg=RGRAY,bd=0,relief='sunken')
console.place(relx=0.05,rely=0.25,relwidth=0.9,relheight=0.5)

info = Label(console,background=RGRAY,fg='#FFFACD',text='Info screen',font=("helvetica", 13))
info.place(relx=0,rely=0.025,relwidth=1)

#information display
display_text = Label(console,background=RGRAY,fg='#E74C3C',font=("helvetica", 10),wraplength=200)
display_text.place(relx=0.1,rely=0.55,relheight=0.8,relwidth=0.8,anchor='w')

loader(target=load_contacts,text='Downloading all contacts from close.com, please wait ...',args={'offset': 0,'limit':100})

#defining start/stop button
start_img = PhotoImage(file = start_img_file)
stop_img = PhotoImage(file = stop_img_file)

start_stop_btn = Button(c_frame,bg=DGRAY, image = start_img,bd=0,borderwidth = 0,highlightthickness=0,command=lambda:loader(target=open_popup,args={'title':'Start operation','header':'click "start" to begin','text':'(Enter phone number in this format:+1234567890)','kind':'start'}))
start_stop_btn.place(relx=0.425,rely=0.825)

attr = Label(root,text='By ihunnaemmanuel@gmail.com, TG:@hustleoclok',bg=DGRAY,fg='#1ABC9C',bd=0,font=("helvetica", 8),highlightthickness=0)
attr.place(relx=0.99,rely=0.99,anchor='se')

def more_or_less(type="more",limit=20):
    global data
    global display_text
    global t_items
    global p_items
    global index
    global present
    global total
    global hold
    if type == "more" and (present < total and index >= 0):index+=1
    elif type == "less" and (present <= total and present > 0) and (index >= 1):index-=1
    else:index = 0
    try:
        data = load_data(index,limit)
        if data[0]:
            total = data[2]
            if type == "more" and present < total:
                present += len(data[1]["data"]) 
            elif type == "less" and (present > 0 and index > 0): 
                present -= len(data[1]["data"])
            else:present = len(data[1]["data"])

            display_text["text"] = "contacts loaded successfully"
            display_text["fg"] = "#F0F0F0"

            t_items["text"] = f"total: {total}"
            p_items["text"] = f"{present}/{total}"

            display_data(data)
        else:
            display_text["fg"] = '#E74C3C'
            display_text["text"] = f"{data[1]}"
    except Exception as error:
        display_text["fg"] = '#E74C3C'
        display_text["text"] = f"{error}"
    hold = False


# add data to the tableview
def display_data(data):
    if data[0]:
        table.delete(*table.get_children())
        for d in data[1]["data"]:
            phone1 = d['phones'][0] if len(d['phones']) > 0 else "None"
            phone2 = d['phones'][1] if len(d['phones']) > 1 else "None"
            if len(d['phones']) > 1: phone = f'[{phone1["phone"]}:{phone1["country"]},{phone2["phone"]},{phone2["country"]}]'
            elif phone1 != 'None': phone = f'{phone1["phone"]}:{phone1["country"]}'
            else:phone = phone1
            table.insert('', 'end',text='value',values=(d['display_name'],d['title'],phone))
            table.tag_configure('colored',font=('TkDefaultFont', 10),foreground='#D0D0D0')
            for item_id in table.get_children():
                table.item(item_id, tags=('colored',))
    else:Label(table,text="No data available",font=("helvetica", 14)).pack(fill=BOTH,expand=True)




# ===================================================================================================
if __name__ == '__main__':
    root.mainloop()