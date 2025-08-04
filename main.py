from pid import *
import customtkinter as ctk
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Frame(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master, width=1000, height=400)
        self.textbox = ctk.CTkTextbox(master=self,width=1000,height=400,font=('Comic Sans MS',15),text_color='Cyan4')
        self.textbox.pack(fill="both",expand=True)

    def insertion(self,msg):
        self.textbox.configure(state='normal')
        self.textbox.insert('end', msg + '\n')
        self.textbox.see('end')
        self.textbox.configure(state='disabled')
        
class Canvas(ctk.CTkCanvas):
    def __init__(self,master):
        super().__init__(master,width=20,height=20,bg='gray16')

class Plotter:
    def display_plot(self,fig):
        for widget in app.frame.winfo_children():
            widget.destroy()

        app.frame.grid(padx=0,pady=0)
        canvas = FigureCanvasTkAgg(fig,master=app.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both',expand=True)
        

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PID Interface")
        self.geometry("1000x600")
        self.resizable(False,False)

        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame = Frame(master=self)
        self.frame.grid(row = 1, column = 0, padx = 20, pady = 20, sticky = "nsew")

        self.button = ctk.CTkButton(self, command=self.clicked,text="Tune Controller",width=60,height=40,border_width=2,
                                    border_color='gray',fg_color='SpringGreen4',hover_color='PaleGreen4',font=('Comic Sans MS',17))
        self.button.grid(row=0,column=0)

        self.titlelabel = ctk.CTkLabel(self,text="PID Tuner",font=('Comic Sans MS',30))
        self.titlelabel.grid(row=0,column=0,padx=113,pady=35,sticky='nw')

        self.statusentry = ctk.CTkEntry(self,placeholder_text='Offline',justify='center',width=90)
        self.statusentry.configure(state='disabled')
        self.statusentry.grid(row=0,column=0,padx=150,pady=40,sticky='sw')

        self.dotcanvas = Canvas(master=self)
        self.dotcanvas.grid(row=0,column=0,padx=120,pady=40,sticky='sw')
        self.circle = self.dotcanvas.create_oval(8,8,18,18, fill='red',outline='white',width=2)

        self.kplabel = ctk.CTkLabel(self,text='KP:',font=('Comic Sans MS',15))
        self.kilabel= ctk.CTkLabel(self,text='KI:',font=('Comic Sans MS',15))
        self.kdlabel = ctk.CTkLabel(self,text='KD:',font=('Comic Sans MS',15))
        self.kplabel.grid(row=0,column=0,sticky='ne',padx=230,pady=30)
        self.kilabel.grid(row=0,column=0,sticky='e',padx=230,pady=40)
        self.kdlabel.grid(row=0,column=0,sticky='se',padx=230,pady=30)

        self.kpentry = ctk.CTkEntry(self,placeholder_text=kp,justify='center',width=150)
        self.kientry = ctk.CTkEntry(self,placeholder_text=ki,justify='center',width=150)
        self.kdentry = ctk.CTkEntry(self,placeholder_text=kd,justify='center',width=150)
        self.kpentry.configure(state='disabled')
        self.kientry.configure(state='disabled')
        self.kdentry.configure(state='disabled')
        self.kpentry.grid(row=0,column=0,sticky='ne',padx=60,pady=30)
        self.kientry.grid(row=0,column=0,sticky='e',padx=60,pady=40)
        self.kdentry.grid(row=0,column=0,sticky='se',padx=60,pady=30)

        plotter = Plotter()
        self.plotbut = ctk.CTkButton(self,text='Plot',state='disabled',command=lambda:plot(plotter.display_plot),width=40,height=20,border_width=2,border_color='gray'
                                     ,fg_color='DodgerBlue3',hover_color='DodgerBlue2',font=('Comic Sans MS',17))
        self.plotbut.grid(row=0,column=0,sticky='s',pady=10)

    def update_values(self,newkp,newki,newkd):
        self.kpentry.configure(state='normal')
        self.kientry.configure(state='normal')
        self.kdentry.configure(state='normal')

        self.kpentry.configure(placeholder_text=newkp)
        self.kientry.configure(placeholder_text=newki)
        self.kdentry.configure(placeholder_text=newkd)

        self.kpentry.configure(state='disabled')
        self.kientry.configure(state='disabled')
        self.kdentry.configure(state='disabled')

    def update_icons(self):
        self.plotbut.configure(state='normal')
        self.dotcanvas.itemconfig(self.circle, fill='green3')
        self.statusentry.configure(state='normal')
        self.statusentry.configure(placeholder_text="Done")
        self.statusentry.configure(state='disabled')

    def clicked(self):    
        self.button.configure(state='disabled')
        self.dotcanvas.itemconfig(self.circle, fill='gold')
        self.statusentry.configure(state='normal')
        self.statusentry.configure(placeholder_text="Tuning")
        self.statusentry.configure(state='disabled')

        t = threading.Thread(target=tuner,args=(kp,ki,kd,self.frame.insertion,self.update_values,self.update_icons))
        t.start()

app = Application()
app.mainloop()


    