from .projects import load_project
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import tkFileDialog
import os, sys, inspect, string, copy, re
import numpy as np
import traceback

__version__ = "0.0.1"






class PopupWindow(object):

    def __init__(self, master=None, title='PopPop'):
        self.pop = tk.Toplevel(master)
        self.pop.title(title)


class InputWindow(ttk.Frame):

    def __init__(self, master=None,title='', text=''):
        self.window = PopupWindow(master=master, title=title).pop

        self.master = master
        self.text = text

        self.stringvar= tk.StringVar()
        self.label=ttk.Label(self.window, text=self.text)
        self.entry = ttk.Entry(self.window, width=50, textvariable=self.stringvar)
        self.okbutton=ttk.Button(self.window,text='OK', command=self.set_variable)
        self.exitbutton=ttk.Button(self.window,text='Exit', command=self.window.destroy)

        self.label.grid(column=0,row=0)
        self.entry.grid(column=1,row=0)
        self.okbutton.grid(column=2,row=0)
        self.exitbutton.grid(column=3,row=0)

    def set_variable(self):
        if self.stringvar.get()!='':
            self.master.variable.set(self.stringvar.get())
            self.window.destroy()


class LoadDirectoryPanel(ttk.Frame):
    #Panel featuring a text field to enter a path, a browse button and an open button. The path of the chosen directory is shown in the text field.
    #When pressing open python changes into the choosen directory if possible (os.chdir) and destroys itself when not called from a master frame or sets the string variable "directory" to the choosen directory else.

    def __init__(self, master=None, labeltext='Directory: ', mastervariable=None):
        ttk.Frame.__init__(self,master)
        if master==None:
            self.frommaster=False
            self.master.title('Load Directory')
            self.pack()
        else:
            self.frommaster=True
        self.mastervariable=mastervariable
        self.labeltext=labeltext

        self.directory=tk.StringVar()
        self.directory.set(os.getcwd())

        self.label=ttk.Label(self, text=self.labeltext)
        self.entry = ttk.Entry(self, width=50,textvariable=self.directory)
        self.openbutton=ttk.Button(self,text='Open', command=self.set_directory)
        self.browsebutton=ttk.Button(self,text='Browse', command=self.get_directory)

        self.label.grid(column=0,row=0)
        self.entry.grid(column=1,row=0)
        self.openbutton.grid(column=2,row=0)
        self.browsebutton.grid(column=3,row=0)

    def get_directory(self):
        self.directory.set(tkFileDialog.askdirectory())
        self.set_directory()

    def set_directory(self):
        os.chdir(self.directory.get())

        if not self.frommaster:
            self.master.destroy()
        else:
            self.mastervariable.set(self.directory.get())


class TreeFrame(ttk.Frame):

    def __init__(self, master=None, columns=[''], data=[''], title='Tree View'):
        ttk.Frame.__init__(self, master)

        if master==None:
            self.frommaster=False
            self.master.title(title)
            self.pack(fill=tk.BOTH,expand=tk.Y)
        else:
            self.frommaster=True

        self.SelectableChildren = True
        self.origselection = ''
        self.descending=True
        self.columns=columns
        self.displaycolumns=self.columns
        self.data=data
        self.treecolumns=[]
        self.create()

        if self.columns!=['']:
            self.populate()

    def on_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.origselection=item
            if self.tree.parent(item) and not self.SelectableChildren:
                pass
            else:
                self.tree.selection_set(item)

    def on_click_ctrl(self,event):
        item = self.tree.identify_row(event.y)
        if item:
            if self.tree.parent(item) and not self.SelectableChildren:
                pass
            else:
                self.tree.selection_add(item)

    def on_click_shift(self,event):
        item = self.tree.identify_row(event.y)
        if item:
            if not self.origselection:
                self.origselection=item
            self.tree.selection_set(self.origselection)
            items = [it for it in self.tree.get_children()]
            items+=[it for ite in self.tree.get_children() for it in self.tree.get_children(ite)]
            items+=[it for ite in self.tree.get_children() for el in self.tree.get_children(ite) for it in self.tree.get_children(el)]
            items = sorted(items)
            if items.index(item) <= items.index(self.tree.selection()[0]):
                items = items[items.index(item):items.index(self.tree.selection()[0])]
            else:
                items = items[items.index(self.tree.selection()[0]):items.index(item)+1]
            for it in items:
                if self.tree.parent(self.tree.parent(it)) and self.tree.item(self.tree.parent(it), option = 'open') == False:
                    pass
                else:
                    self.tree.selection_add(it)

    def create(self):
        self.tree = ttk.Treeview(self, columns=self.columns, displaycolumns=self.displaycolumns, show = 'headings', selectmode='none')
        ysb = ttk.Scrollbar(orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set

        # add tree and scrollbars to frame
        self.tree.grid(in_=self, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self, row=1, column=0, sticky=tk.EW)

        # set frame resizing priorities
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        #handle what happens if objet is selected
        self.tree.bind('<Button-1>', self.on_click)
        self.tree.bind('<Control-1>', self.on_click_ctrl)
        self.tree.bind('<Shift-1>', self.on_click_shift)

    def _getlist(self, elem):
        ch=[0]*len(elem)
        for i in range(0,len(elem)):
            if isinstance(elem[i],list):
                ch[i]=len(elem[i])
        return ch

    def recreate(self):
        self.tree.destroy()
        self.treecolumns=[]
        self.create()
        if self.columns!=['']:
            self.populate()

    def update(self, newdisplaycolumns):
        if not set(newdisplaycolumns)<=set(self.columns):
            print 'Unable to update Tree!'
            return
        else:
            self.displaycolumns=newdisplaycolumns
            self.tree.configure(displaycolumns=self.displaycolumns)

    def populate(self):
        self.maxcolwidth=[0]*len(self.columns)
        for column in self.columns:
            self.tree.heading(column, text=column.title(), command=lambda column=column: self._column_sort(column, self.descending))

            self.treecolumns.append(self.tree.column(column, minwidth=Font().measure(column.title())))
            self.maxcolwidth[self.columns.index(column)]=Font().measure(column.title())
        for item in self.data:
            itch=self._getlist(item)

            if not all(el ==0 for el in itch):

                changeditem=['' if itch[i] != 0 else item[i] for i in range(0,len(item))]

                parent=self.tree.insert('','end',values=changeditem)
                meas=[Font().measure(str(el)) for el in changeditem]
                self.maxcolwidth=[meas[i] if meas[i]>self.maxcolwidth[i] else self.maxcolwidth[i] for i in range(0,len(self.maxcolwidth))]


                for i in range(0,max(itch)):
                    #childitem=['' if itch[j] ==0 or itch[j]<i else item[j][i] for j in range(0,len(item))]
                    #childitem=['' if itch[j] ==0 or itch[j]<i else item[j][i] if not isinstance(item[j][i],list) else item[j][i][-1][:re.search('\d', item[j][i][-1]).start()] for j in range(0,len(item))]
                    #childitem=['' if itch[j] ==0 or itch[j]<i else item[j][i] if not isinstance(item[j][i],list) else item[j][i][-1][:item[j][i][-1].rfind('0')]+'...'+item[j][i][-1][item[j][i][-1].rfind('.'):] for j in range(0,len(item))]
                    childitem=['' if itch[j] ==0 or itch[j]<i else item[j][i] if not isinstance(item[j][i],list) else re.sub(re.findall('\d+',item[j][i][0])[-1],'.',item[j][i][0]) for j in range(0,len(item))]
                    child=self.tree.insert(parent,'end',values=childitem)
                    meas=[Font().measure(el) for el in childitem]

                    self.maxcolwidth=[meas[k] if meas[k]>self.maxcolwidth[k] else self.maxcolwidth[k] for k in range(0,len(self.maxcolwidth))]

                    for j in range(0,len(item)):
                        if itch[j]!=0 and itch[j]>i:
                            if isinstance(item[j][i],list):
                                for k in range(0,len(item[j][i])):
                                    grandchilditem=['' if itch[l] ==0 or itch[l]<i else item[j][i][k] for l in range(0,len(item))]
                                    self.tree.insert(child, 'end',values=grandchilditem)



            else:
                parent=self.tree.insert('', 'end', values=list(item))


                meas=[Font().measure(el) for el in item]
                self.maxcolwidth=[meas[i] if meas[i]>self.maxcolwidth[i] else self.maxcolwidth[i] for i in range(0,len(self.maxcolwidth))]

        for j in range(0,len(self.columns)):
            self.tree.column(self.columns[j],width=self.maxcolwidth[j])

    def _column_sort(self, col, descending=False):
        # grab values to sort as a list of tuples (column value, column id)
        # e.g. [('Argentina', 'I001'), ('Australia', 'I002'), ('Brazil', 'I003')]
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        # reorder data
        # tkinter looks after moving other items in
        # the same row
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            self.tree.move(item[1], '', indx)   # item[1] = item Identifier

        # reverse sort direction for next sort operation
        self.descending = not descending

    def get_selection(self):
        self.selectionlist=[[[],[]]]
        for element in self.tree.selection():
            if self.tree.parent(element):
                if self.tree.parent(self.tree.parent(element)):
                    elementrecord=self.tree.item(self.tree.parent(self.tree.parent(element)))['values'][self.columns.index('label')]
                    elementdata=[self.tree.item(element)['values'][self.columns.index('output_data')]]
                else:
                    elementrecord=self.tree.item(self.tree.parent(element))['values'][self.columns.index('label')]
                    if self.tree.get_children(element):
                        elementdata=[[self.tree.item(el)['values'][self.columns.index('output_data')] for el in self.tree.get_children(element)]]
                    else:
                        elementdata=[self.tree.item(element)['values'][self.columns.index('output_data')]]
                        #if not self.tree.get_children(element):
                    #    elementdata=[self.tree.item(element)['values'][self.columns.index('output_data')]]
                    #else:
                    #    elementdata=[self.tree.item(el)['values'][self.columns.index('output_data')] for el in self.tree.get_children(element)]
            else:
                #Case no parent -> output of whole record wanted -> select all items
                elementrecord=self.tree.item(element)['values'][self.columns.index('label')]
                elementdata=[]
                for el in self.tree.get_children(element):
                    if self.tree.get_children(el):
                        elementdata+=[[self.tree.item(ele)['values'][self.columns.index('output_data')] for ele in self.tree.get_children(el)]]
                    else:
                        elementdata+=[self.tree.item(el)['values'][self.columns.index('output_data')]]
                #elementdata=[self.tree.item(el)['values'][self.columns.index('output_data')] for el in self.tree.get_children(element)]
            if not elementrecord in zip(*self.selectionlist)[0]:
                self.selectionlist.append([elementrecord,elementdata])
            else:
                self.selectionlist[zip(*self.selectionlist)[0].index(elementrecord)][1] += [el for el in elementdata if el not in self.selectionlist[zip(*self.selectionlist)[0].index(elementrecord)][1]]
        self.selectionlist=self.selectionlist[1:]


class CheckBoxPanel(ttk.Frame):

    def __init__(self, master=None, title='CheckBox Panel', checkboxnames=[], selectedboxes=[], mastervariable=None):
        ttk.Frame.__init__(self,master)
        if master==None:
            self.frommaster=False
            self.master.title(title)
            self.pack()
        else:
            self.frommaster=True
        self.mastervariable=mastervariable

        self.checkboxnames=checkboxnames
        self.selectedboxes=selectedboxes
        self.checkvariables=[]
        self.checkboxes=[]

        self.update()

    def update(self):
        self.checkvariables=[]
        for box in self.checkboxes:
            box.destroy()
        self.checkboxes=[]
        for i in range(0,len(self.checkboxnames)):
            self.checkvariables.append(tk.IntVar())
            self.checkboxes.append(ttk.Checkbutton(self,text=self.checkboxnames[i],command=self.returning, variable=self.checkvariables[i]))
            if self.checkboxnames[i] in self.selectedboxes:
                self.checkvariables[i].set(1)
            self.checkboxes[i].pack(anchor='nw')

    def unselectall(self):
        for i in range(0,len(self.checkboxnames)):
            if self.checkvariables[i].get()==1:
                self.checkboxes[i].invoke()

    def clear(self):
        self.unselectall()
        self.checkboxnames=[]
        self.checkboxvariables=[]
        for box in self.checkboxes:
            box.destroy()

    def disable(self, checkboxname):
        #Disable a checkbox (not checkable anymore) and grey it
        for checkbox in self.checkboxes:
            if checkbox['text']==checkboxname:
                checkbox.config(state=tk.DISABLED)
                break

    def enable(self, checkboxname):
        #Enable a checkbox to be checked
        for checkbox in self.checkboxes:
            if checkbox['text']==checkboxname:
                checkbox.config(state=tk.NORMAL)
                break

    def returning(self):
        for i in range(0,len(self.checkvariables)):
            if self.checkboxnames[i] in self.selectedboxes and self.checkvariables[i].get()==0:
                self.selectedboxes.remove(self.checkboxnames[i])
                if self.mastervariable:
                    self.mastervariable.set(self.checkboxnames[i])
            elif self.checkboxnames[i] not in self.selectedboxes and self.checkvariables[i].get()==1:
                self.selectedboxes.append(self.checkboxnames[i])
                if self.mastervariable:
                    self.mastervariable.set(self.checkboxnames[i])


class SumatraGui(ttk.Frame):


    ShowFileEndings = 'all'
    SelectableChildren = True

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(4, weight=1)

        self.treeset=0
        self.descending=True
        self.archiverecordstore=False

        self.directory=tk.StringVar()

        self.projectstatustext=tk.StringVar()
        self.projectstatustext.set("No project loaded!")

        self.standardcolumns=['label','timestamp','tags','reason','parameters','output_data']

        self.changecolumn=tk.StringVar()
        self.optionsvar=tk.StringVar()
        self.parametersvar=tk.StringVar()
        self.init_window()

        self.changecolumn.trace(mode='w', callback=self.update_tree)
        self.parametersvar.trace(mode='w', callback=self.update_tree)
        self.optionsvar.trace(mode='w', callback=self.options)
        self.directory.trace(mode='w',callback=self.load_project)

        self.directory.set(os.getcwd())

    def init_window(self):
        self.projectpanel=ttk.Frame(self)
        self.projectpanel.grid(row=0,column=0, sticky=(tk.N, tk.W, tk.S, tk.E))

        self.directoryloadpanel=LoadDirectoryPanel(self.projectpanel, labeltext="Project Directory: ", mastervariable=self.directory)
        self.directoryloadpanel.grid(row=0,column=0, sticky=(tk.N, tk.W))

        self.projectstatuslabelframe=ttk.Frame(self.projectpanel)
        self.projectstatuslabelframe.grid(row=1, column=0)

        self.projectstatuslabel=ttk.Label(self.projectstatuslabelframe, textvariable=self.projectstatustext, font='TkCaptionFont')
        self.projectstatuslabel.grid(sticky=(tk.N, tk.S, tk.W, tk.E))

        self.projectoptionsinset=ttk.Frame(self.projectpanel, borderwidth=1, relief=tk.SOLID)
        ttk.Label(self.projectoptionsinset, text='Project Options').pack(anchor='w')
        self.projectoptionscheckboxpanel=CheckBoxPanel(self.projectoptionsinset, mastervariable=self.optionsvar)
        self.projectoptionscheckboxpanel.checkboxnames=['Expand Parameters']
        self.projectoptionscheckboxpanel.update()
        self.projectoptionscheckboxpanel.pack()

        self.checkboxpanel=CheckBoxPanel(self, mastervariable=self.changecolumn)

        self.parametercheckboxpanel=CheckBoxPanel(self, mastervariable=self.parametersvar)
        self.parametercheckboxpanelstatus=0

        self.treepanel=TreeFrame(self)
        self.treepanel.grid(row=1,column=0, sticky=(tk.N, tk.S, tk.E, tk.W), columnspan=5)

        self.ButtonFrame=ttk.Frame(self)
        self.okbutton=ttk.Button(self.ButtonFrame,text='OK', command=self.finish)
        self.okbutton.grid(row=0, column=0)
        self.exitbutton=ttk.Button(self.ButtonFrame,text='Exit', command=self.master.destroy)
        self.exitbutton.grid(row=0,column=1)
        self.ButtonFrame.grid(row=2, column=4, sticky=(tk.S, tk.E))

    def load_project(self, varname, elementname, mode):
        try:
            self.project=load_project()
            if hasattr(self.project.data_store, 'move_store'):
                self.projectdatastore=os.path.expanduser(str(self.project.data_store)[str(self.project.data_store).find('to')+3:-1])
            else:
                self.projectrecordstore=os.path.expanduser(str(self.project.data_store))
            self.projectstatustext.set('Project "'+str(self.project.name)+'" loaded')
        except:
            traceback.print_exc()
            self.project=''
            self.projectstatustext.set('Unable to find Sumatra project inside given directory!')
            self.treepanel.columns=['']
            self.treepanel.displaycolumns=['']
            self.treepanel.data=['']
            self.treepanel.recreate()
            self.checkboxpanel.grid_forget()
            self.parametercheckboxpanel.grid_forget()
            self.projectoptionsinset.grid_forget()
            self.projectoptionscheckboxpanel.unselectall()
        if self.project:
            if self.get_project_data() != 0:
                self.projectoptionsinset.grid(row=2, column=0, sticky=tk.NSEW)
                self.process_data()
                self.parametercheckboxpanel.checkboxnames=self.parameters
                self.parametercheckboxpanel.selectedboxes=self.parameters
                self.parametercheckboxpanel.update()
                self.checkboxpanel.checkboxnames=[item for item in self.showdataheader if item not in self.parameters]
                self.checkboxpanel.selectedboxes=list(self.standardcolumns)
                self.checkboxpanel.update()
                self.visibledata=copy.deepcopy(self.standardcolumns)
                self.treepanel.columns=self.showdataheader
                self.treepanel.displaycolumns=self.visibledata
                self.treepanel.data=list(zip(*self.showdata))
                #self.treepanel.grid_forget()
                self.treepanel.recreate()
                self.checkboxpanel.grid(row=0,column=2)
            else:
                self.treepanel.columns=['']
                self.treepanel.displaycolumns=['']
                self.treepanel.data=['']
                self.treepanel.recreate()
                self.checkboxpanel.grid_forget()
                self.parametercheckboxpanel.grid_forget()
                self.projectoptionsinset.grid_forget()
                self.projectoptionscheckboxpanel.unselectall()

    def get_project_data(self):
        try:
            self.records=self.project.record_store.list(self.project.name)
        except:
            traceback.print_exc()
            self.projectstatustext.set('Unable to load records for Sumatra project '+str(self.project.name)+'!')
            return 0
        if not self.records:
            self.projectstatustext.set('Project "'+self.project.name+'" has no records to show!')
            return 0
        self.datalabels=self.records[0].__dict__.keys()
        self.removecolumns=['platforms','repository','datastore','input_datastore','dependencies','stdout_stderr']

        self.datalist=[self.datalabels.index(element) for element in self.datalabels if element not in self.removecolumns]
        self.projectdata=[np.array(self.records[i].__dict__.values())[self.datalist] for i in range(0,len(self.records))]
        self.datalabels=[element for element in self.datalabels if element not in self.removecolumns]
        return 1

    def process_data(self):
        self.showdata=list(copy.deepcopy(self.projectdata))
        self.showdataheader=copy.deepcopy(self.datalabels)
        if 'tags' in self.showdataheader:

            for element in self.showdata:
                if not element[self.showdataheader.index('tags')]:
                    element[self.showdataheader.index('tags')]=''

                else:
                    element[self.showdataheader.index('tags')]=' '.join(element[self.showdataheader.index('tags')])
        '''
        if 'parameters' in self.showdataheader:

            for element in self.showdata:

                if not element[self.showdataheader.index('parameters')]:
                    element[self.showdataheader.index('parameters')]=''

                else:
                    #element[self.showdataheader.index('parameters')]=' '.join(element[self.showdataheader.index('parameters')])

                    if isinstance(element[self.showdataheader.index('parameters')].as_dict().values()[0],dict):

                        paramdict=element[self.showdataheader.index('parameters')].as_dict().values()[0]

                        for i in range(1,len(element[self.showdataheader.index('parameters')].as_dict().values())):
                            paramdict.update(element[self.showdataheader.index('parameters')].as_dict().values()[i])
                        element[self.showdataheader.index('parameters')]=', '.join('{} = {}'.format(key,val) for key, val in sorted(paramdict.items()))
                    #element[self.showdataheader.index('parameters')]=element[self.showdataheader.index('parameters')].as_dict()
        '''
        if 'input_data' in self.showdataheader:

            for element in self.showdata:

                if not element[self.showdataheader.index('input_data')]:
                    element[self.showdataheader.index('input_data')]=''

        if 'output_data' in self.showdataheader:

            for element in self.showdata:

                if not element[self.showdataheader.index('output_data')]:
                    element[self.showdataheader.index('output_data')]=''
                else:
                    changed=[]
                    for j in range(0,len(element[self.showdataheader.index('output_data')])):

                        element[self.showdataheader.index('output_data')][j]=str(element[self.showdataheader.index('output_data')][j].path)
                        element[self.showdataheader.index('output_data')][j]=element[self.showdataheader.index('output_data')][j][element[self.showdataheader.index('output_data')][j].find('/')+1:]

                        if self.ShowFileEndings == 'all' or element[self.showdataheader.index('output_data')][j][element[self.showdataheader.index('output_data')][j].rfind('.')+1:] in self.ShowFileEndings:
                            changed.append(element[self.showdataheader.index('output_data')][j])

                    element[self.showdataheader.index('output_data')]=changed

                    files=element[self.showdataheader.index('output_data')]

                    files=[fil for fil in files if any(char.isdigit() for char in fil)]

                    endings=list(set([fil[fil.rfind('.')+1:] for fil in files]))# if fil[fil.rfind('.')+1:] not in endings]

                    sets=[]
                    for ends in endings:
                        tempfiles=[fil[:fil.rfind('.')] for fil in files if fil[fil.rfind('.')+1:]==ends]
                        beginnings=list(set([fil[:re.search('\d',fil).start()] for fil in tempfiles]))
                        for begs in beginnings:
                            temp=[fil+'.'+ends for fil in tempfiles if fil[:re.search('\d',fil).start()]==begs]
                            if len(temp) > 1:
                                sets.append(sorted(temp))
                    allsubs=[item for sub in sets for item in sub]
                    element[self.showdataheader.index('output_data')]=sets+[el for el in element[self.showdataheader.index('output_data')] if el not in allsubs]

        self.showdata=list(zip(*self.showdata))

        if 'parameters' in self.showdataheader:
            index = self.showdataheader.index('parameters')
            self.showdata[index]=list(self.showdata[index])
            self.parameters=[]
            for i in range(0,len(self.showdata[index])):
                if not self.showdata[index][i]:
                    self.showdata[index][i]=''
                else:
                    # Collect parameters
                    self.parameters += get_keys(self.showdata[index][i].as_dict())
            self.parameters = list(set(self.parameters))
            self.showdataheader+=self.parameters
            self.showdata+=[['' for i in range(len(self.showdata[0]))] for j in range(len(self.parameters))]
            self.showdata[18][0]='ha'
            for i in range(0,len(self.showdata[index])):
                if self.showdata[index][i]:
                    dic=flatten_dict(self.showdata[index][i].as_dict())
                    params=dic.keys()
                    for j in range(0,len(params)):
                        self.showdata[self.showdataheader.index(params[j])][i]=str(dic[params[j]])
                    self.showdata[index][i]=', '.join('{} = {}'.format(key,val) for key, val in sorted(dic.items()))
        for i in range(0,len(self.standardcolumns)):
            if self.showdataheader[i]!=self.standardcolumns[i]:
                swapindex=self.showdataheader.index(self.standardcolumns[i])
                self.showdataheader[swapindex], self.showdataheader[i] = self.showdataheader[i], self.showdataheader[swapindex]
                self.showdata[swapindex], self.showdata[i] = self.showdata[i], self.showdata[swapindex]

    def update_tree(self, varname, elementname, mode):
        column = self.master.globalgetvar(varname)
        comparecolumn=''
        if not self.visibledata:
            self.visibledata.append(column)
        else:
            if column in self.visibledata:
                self.visibledata.remove(column)
            else:
                if column in self.parameters:
                    if not set(self.parameters).isdisjoint(set(self.visibledata)):
                        found=False
                        for i in range(len(self.visibledata)):
                            if self.visibledata[i] in self.parameters:
                                if not found:
                                    found=True
                                if self.parameters.index(column) < self.parameters.index(self.visibledata[i]):
                                    self.visibledata.insert(i,column)
                                    break
                            else:
                                if found:
                                    self.visibledata.insert(i,column)
                                    break
                    else:
                        comparecolumn='parameters'
                else:
                    comparecolumn=column
            if comparecolumn:
                if comparecolumn in self.standardcolumns:#is it a standard element?
                    if self.visibledata[0] in self.standardcolumns: #are there standard elements shown right now?
                        inserted=False
                        for entry in self.visibledata:
                            try:
                                if self.standardcolumns.index(comparecolumn) < self.standardcolumns.index(entry):
                                    selfvisibledata.insert(self.visibledata.index(entry),column)
                                    inserted=True
                                    break
                            except:
                                self.visibledata.insert(self.visibledata.index(entry),column)
                                inserted=True
                                break
                        if not inserted:
                            self.visibledata.append(column)
                    else:
                        self.visibledata.insert(0,column)
                else:
                    self.visibledata.append(column)
        self.treepanel.update(self.visibledata)

    def options(self, varname, elementname, mode):
        if self.optionsvar.get()=='Expand Parameters':
            if self.parametercheckboxpanelstatus==0:
                self.parametercheckboxpanel.grid(row=0, column=3)
                self.parametercheckboxpanelstatus=1
                if 'parameters' in self.visibledata:
                    self.visibledata.remove('parameters')
                self.visibledata+=[element for element in self.parameters if element in self.parametercheckboxpanel.selectedboxes]
                self.checkboxpanel.disable('parameters')
                self.treepanel.update(self.visibledata)
            else:
                self.parametercheckboxpanel.grid_forget()
                self.parametercheckboxpanelstatus=0
                self.visibledata=[element for element in self.visibledata if element not in self.parameters]
                if 'parameters' in self.checkboxpanel.selectedboxes:
                    if self.visibledata[0] in self.standardcolumns: #are there standard elements shown right now?
                        if self.standardcolumns.index('parameters') < self.standardcolumns.index(self.visibledata[0]):
                            self.visibledata.insert(0,'parameters')
                        else:
                            for entry in self.visibledata:
                                try:
                                    if self.standardcolumns.index('parameters') < self.standardcolumns.index(entry):
                                        selfvisibledata.insert(self.visibledata.index(entry),'parameters')
                                        break
                                except:
                                    self.visibledata.insert(self.visibledata.index(entry),'parameters')
                                    break
                    else:
                        self.visibledata.insert(0,'parameters')
                self.treepanel.update(self.visibledata)
                self.checkboxpanel.enable('parameters')

    def before_finish(self):
        # Here something that happens then the user presses ok should be implemented. Thoughts are that in the future records can be erase from the gui and stuff like that. Major changes like erasing records shouldbe done only temporariliy in the gui. After pressing ok, the major changes should be listed again and the user should be asked to confirm them again.
        pass

    def finish(self):
        self.treepanel.get_selection()
        self.before_finish()
        self.master.destroy()

def get_keys(dic):
    return [val for sublist in [get_keys(el) for el in dic.values() if isinstance(el,dict)] for val in sublist] + [dic.keys()[i] for i in range(0, len(dic.values())) if not isinstance(dic.values()[i], dict)]

def flatten_dict(dic):
    new_dict={}
    for key,value in dic.iteritems():
        if isinstance(value,dict):
            new_dict.update(flatten_dict(value))
        else:
            new_dict.update({key: value})
    return new_dict
