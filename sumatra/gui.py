from .projects import load_project
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import tkFileDialog
import os, sys, inspect, string, copy, re
import numpy as np


class PopupWindow(object):

    def __init__(self, master=None, title='PopPop'):

        self.pop = tk.Toplevel(master)
        self.pop.title(title)


class InputWindow(tk.Frame):

    def __init__(self, master=None,title='', text=''):

        self.window = PopupWindow(master=master, title=title).pop

        self.master = master
        self.text = text

        self.stringvar= tk.StringVar()
        self.label=tk.Label(self.window, text=self.text)
        self.entry = tk.Entry(self.window, width=50, textvariable=self.stringvar)
        self.okbutton=tk.Button(self.window,text='OK', command=self.set_variable)
        self.exitbutton=tk.Button(self.window,text='Exit', command=self.window.destroy)

        self.label.grid(column=0,row=0)
        self.entry.grid(column=1,row=0)
        self.okbutton.grid(column=2,row=0)
        self.exitbutton.grid(column=3,row=0)
 
    def set_variable(self):
        if self.stringvar.get()!='':
            self.master.variable.set(self.stringvar.get())
            self.window.destroy()

class LoadDirectoryPanel(tk.Frame):
    #Panel featuring a text field to enter a path, a browse button and an open button. The path of the chosen directory is shown in the text field.
    #When pressing open python changes into the choosen directory if possible (os.chdir) and destroys itself when not called from a master frame or sets the string variable "directory" to the choosen directory else.

    def __init__(self, master=None,labeltext='Directory: '):
        tk.Frame.__init__(self,master)

        if master==None:
            self.frommaster=False
            self.master.title('Load Directory')
            self.pack()
        else:
            self.frommaster=True

        self.labeltext=labeltext

        self.directory=tk.StringVar()
        self.directory.set(os.getcwd())

        self.label=tk.Label(self, text=self.labeltext)
        self.entry = tk.Entry(self, width=50,textvariable=self.directory)
        self.openbutton=tk.Button(self,text='Open', command=self.set_directory)
        self.browsebutton=tk.Button(self,text='Browse', command=self.get_directory)

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

            self.master.directory.set(self.directory.get())



class TreeFrame(tk.Frame):

    def __init__(self, master=None, columns=[''], data=[''], title='Tree View'):
        tk.Frame.__init__(self, master)
        if master==None:
            self.frommaster=False
            self.master.title(title)
            self.pack(fill=tk.BOTH,expand=tk.Y)
        else:
            self.frommaster=True
        self.SelectableChildren = True
        self.descending=True
        self.columns=columns
        self.data=data
        self.treecolumns=[]
        self.create()
        if self.columns!=['']:
            self.populate()


    def on_click(self, event):
        #tree = event.widget
        item = self.tree.identify_row(event.y)
        if self.tree.parent(item) and not self.SelectableChildren:
            pass
        else:
            self.tree.selection_set(item)


    def on_click_ctrl(self,event):
        #tree = event.widget
        item = self.tree.identify_row(event.y)
        if self.tree.parent(item) and not self.SelectableChildren:
            pass
        else:
            self.tree.selection_add(item)


    def create(self):
        self.tree = ttk.Treeview(self, columns=self.columns, show = 'headings', selectmode='none')
        ysb = tk.Scrollbar(orient=tk.VERTICAL, command=self.tree.yview)
        xsb = tk.Scrollbar(orient=tk.HORIZONTAL, command=self.tree.xview)
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


    def _getlist(self, elem):
        ch=[0]*len(elem)
        for i in range(0,len(elem)):
            if isinstance(elem[i],list):
                ch[i]=len(elem[i])
        return ch


    def update(self):
        self.tree.destroy()
        self.treecolumns=[]
        self.create()
        self.populate()


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

                meas=[Font().measure(el) for el in changeditem]
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
        '''
        for element in self.tree.selection():
            if self.tree.parent(element):
                if self.tree.parent(self.tree.parent(element)):
                    print 'here'
                    self.selectionlist.append(os.path.join(self.tree.item(self.tree.parent(self.tree.parent(element)))['values'][self.columns.index('label')],self.tree.item(element)['values'][self.columns.index('output_data')]))
                elif self.tree.get_children(element):
                    self.selectionlist.append([os.path.join(self.tree.item(self.tree.parent(element))['values'][self.columns.index('label')],self.tree.item(el)['values'][self.columns.index('output_data')]) for el in self.tree.get_children(element)])
                    #self.selectionlist.append(os.path.join(self.tree.item(self.tree.parent(element))['values'][self.columns.index('label')],self.tree.item(element)['values'][self.columns.index('output_data')]))

                else:
                    self.selectionlist.append(os.path.join(self.tree.item(self.tree.parent(element))['values'][self.columns.index('label')],self.tree.item(element)['values'][self.columns.index('output_data')]))
            else:
                self.selectionlist=self.selectionlist+[os.path.join(self.tree.item(element)['values'][self.columns.index('label')],self.tree.item(el)['values'][self.columns.index('output_data')]) for el in  self.tree.get_children(element)]
        print self.selectionlist
        '''
class CheckBoxPanel(tk.Frame):

    def __init__(self, master=None, title='CheckBox Panel', checkboxnames=[], selectedboxes=[]):
        tk.Frame.__init__(self,master)
        if master==None:
            self.frommaster=False
            self.master.title(title)
            self.pack()
        else:
            self.frommaster=True

        self.checkboxnames=checkboxnames
        self.selectedboxes=selectedboxes
        self.checkvariables=[]
        self.checkboxes=[]

        self.update()


    def update(self):
        for i in range(0,len(self.checkboxnames)):
            self.checkvariables.append(tk.IntVar())
            self.checkboxes.append(tk.Checkbutton(self,text=self.checkboxnames[i],command=self.returning, variable=self.checkvariables[i]))
            if self.checkboxnames[i] in self.selectedboxes:
                self.checkboxes[i].select()
            self.checkboxes[i].pack(anchor='nw')


    def returning(self):
        for i in range(0,len(self.checkvariables)):
            if self.checkboxnames[i] in self.selectedboxes and self.checkvariables[i].get()==0:
                self.selectedboxes.remove(self.checkboxnames[i])
                self.master.changecolumn.set(self.checkboxnames[i])
            elif self.checkboxnames[i] not in self.selectedboxes and self.checkvariables[i].get()==1:
                self.selectedboxes.append(self.checkboxnames[i])
                self.master.changecolumn.set(self.checkboxnames[i])



class SumatraTree(tk.Frame):


    ShowFileEndings = 'all'
    SelectableChildren = True

    def __init__(self, title='Sumatra'):
        tk.Frame.__init__(self)
        self.master.title(title)
        self.pack(fill=tk.BOTH, expand=tk.Y, anchor='nw')

        self.treeset=0
        self.descending=True
        self.archiverecordstore=False

        self.directory=tk.StringVar()

        self.projectstatustext=tk.StringVar()
        self.projectstatustext.set("No project loaded!")

        self.standardcolumns=['label','timestamp','tags','reason','parameters','output_data']

        self.changecolumn=tk.StringVar()

        self.init_window()

        self.changecolumn.trace(mode='w', callback=self.update_tree)
        self.directory.trace(mode='w',callback=self.load_project)

        self.directory.set(os.getcwd())


    def init_window(self):
        self.mydirectoryloadpanel=LoadDirectoryPanel(self, labeltext="Project Directory: ")
        self.mydirectoryloadpanel.pack(anchor='nw')

        self.projectoptionspanel=tk.Frame(self)
        self.projectoptionspanel.pack(fill=tk.X)

        self.projectstatuslabelframe=tk.Frame(self.projectoptionspanel)
        self.projectstatuslabelframe.pack(side=tk.LEFT,expand=True,fill=tk.X)

        self.projectstatuslabel=tk.Label(self.projectstatuslabelframe, textvariable=self.projectstatustext)
        self.projectstatuslabel.pack(side=tk.LEFT,expand=True,fill=tk.X)


        self.checkboxpanel=CheckBoxPanel(self)
        self.checkboxpanel.pack(side=tk.LEFT)

        self.treepanel=TreeFrame(self)
        self.treepanel.pack(fill=tk.BOTH, expand=tk.Y)
        self.treepanel.SelectableChildren = self.SelectableChildren

        self.ButtonFrame=tk.Frame(self)
        self.okbutton=tk.Button(self.ButtonFrame,text='OK', command=self.finish)
        self.okbutton.pack(side=tk.LEFT)
        self.exitbutton=tk.Button(self.ButtonFrame,text='Exit', command=self.master.destroy)
        self.exitbutton.pack(side=tk.LEFT)
        self.ButtonFrame.pack(anchor='e')


    def load_project(self, varname, elementname, mode):
        #try:
        self.project=load_project()
        self.projectrecordstore=str(self.project.data_store)[str(self.project.data_store).find('to')+3:-1]
        self.projectstatustext.set('Project "'+str(self.project.name)+'" loaded')

        #prevents the projectoptionsinset to be created several times
        try:
            self.projectoptionsinset
        except:
            self.projectoptionsinset=tk.Frame(self.projectoptionspanel, bd=1, relief=tk.SOLID)
            self.projectoptionsinset.pack(side=tk.RIGHT,expand=True,fill=tk.X)

            tk.Label(self.projectoptionsinset, text='Project Options').pack(anchor='w')
            self.projectoptionscheckboxpanel=CheckBoxPanel(self.projectoptionsinset)
            self.projectoptionscheckboxpanel.checkboxnames=['Expand Parameters']
            self.projectoptionscheckboxpanel.update()
            self.projectoptionscheckboxpanel.pack()


        if self.get_project():
            self.process_data()
        else:
            self.projectstatustext.set('Project "'+self.project.name+'" has no records to show!')
        #except:
        #    self.projectstatustext.set('Unable to find Sumatra project inside given directory!')


    def get_project(self):
        self.records=self.project.record_store.list(self.project.name)
        if not self.records:
            return 0

        self.dataheader=self.records[0].__dict__.keys()
        self.removecolumns=['platforms','repository','datastore','input_datastore','dependencies','stdout_stderr']

        self.datalist=[self.dataheader.index(element) for element in self.dataheader if element not in self.removecolumns]

        self.projectdata=[np.array(self.records[i].__dict__.values())[self.datalist] for i in range(0,len(self.records))]

        self.dataheader=[element for element in self.dataheader if element not in self.removecolumns]
        self.checkboxpanel.checkboxnames=list(self.dataheader)
        self.checkboxpanel.selectedboxes=list(self.standardcolumns)
        for element in self.standardcolumns:
            self.checkboxpanel.checkboxnames.remove(element)

        self.checkboxpanel.checkboxnames=list(self.standardcolumns+self.checkboxpanel.checkboxnames)
        self.checkboxpanel.update()

        self.showdatalist=[]

        for element in self.standardcolumns:
            self.showdatalist.append(self.dataheader.index(element))

        return 1

    def update_tree(self, varname, elementname, mode):
        if self.changecolumn.get() in self.showdataheader:
            self.showdatalist.remove(self.dataheader.index(self.changecolumn.get()))
        else:
            if self.changecolumn.get() in self.standardcolumns:#is it a standard element?
                if self.dataheader[self.showdatalist[0]] in self.standardcolumns: #are there standard elements shown right now?
                    for i in range(0,len(self.standardcolumns)):
                        try:
                            if self.standardcolumns.index(self.changecolumn.get()) < self.standardcolumns.index(self.dataheader[self.showdatalist[i]]):
                                self.showdatalist.insert(i,self.dataheader.index(self.changecolumn.get()))
                                break
                        except:
                            self.showdatalist.insert(i,self.dataheader.index(self.changecolumn.get()))
                            break
                else:
                    self.showdatalist.insert(0,self.dataheader.index(self.changecolumn.get()))
            else:
                self.showdatalist.append(self.dataheader.index(self.changecolumn.get()))

        self.process_data()
        self.treepanel.update()


    def process_data(self):
        self.showdata=list(copy.deepcopy([self.projectdata[i][self.showdatalist] for i in range(0,len(self.projectdata))]))
        self.showdataheader=list(np.array(self.dataheader)[self.showdatalist])

        if 'tags' in self.showdataheader:

            for element in self.showdata:
                if not element[self.showdataheader.index('tags')]:
                    element[self.showdataheader.index('tags')]=''

                else:
                    element[self.showdataheader.index('tags')]=' '.join(element[self.showdataheader.index('tags')])

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

        self.treepanel.columns=self.showdataheader
        self.treepanel.data=self.showdata

        self.treepanel.update()

    def before_finish(self):
        pass

    def finish(self):
        self.treepanel.get_selection()
        self.before_finish()
        #self.load_selection()
        #self.master.destroy()
