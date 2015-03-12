from Tkinter import *
import socket
import ssl
import xml.etree.ElementTree as ET
import thread
import logging
import base64
import re

LOGGING_FILE = 'xmpp_client.log'
logging.basicConfig(filename=LOGGING_FILE,
                    level=logging.DEBUG,
                    )




class pyApp:
    
    def __init__(self, parent):
        self.container = parent
        self.frame1 = Frame(self.container)
        self.frame1.pack()
        self.label1 = Label(self.frame1, text="UserID")
        self.label1.pack(ipadx=30, ipady=30)
        self.id = Entry(self.frame1, width=30)
        self.usrname=""
        self.passwd=""
        self.id.pack()
        self.label2 = Label(self.frame1, text="Password")
        self.label2.pack(ipadx=30, ipady=30)
        self.pswd = Entry(self.frame1, width=30)
        self.pswd.pack()
        self.submit = Button(self.frame1, text="Submit", command=self.afterSubmit)
        self.submit.pack()
        self.sock=None
        self.domain=""
        self.writeMsgTexts = {}
        self.conversationBoxes = {}
        self.contact_positions={}
        self.createdframes={}
        self.typinglabels = {}
        
    #This method returns the contact list by quering it from the server.
    def getroster(self):
        BUFFER_SIZE=4096
        client_message = "<stream:stream to='"+self.domain+"' xmlns:stream='http://etherx.jabber.org/streams' xmlns='jabber:client' xml:lang='en' version='1.0'>"
        self.sock.send(client_message)
        logging.debug('Client:')
        logging.debug(client_message)

        server_response = self.sock.recv(BUFFER_SIZE)
        logging.debug('Server:')
        logging.debug(server_response)
        #print "received server_response:", server_response
        
        client_message = "<iq type='set' id='0'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind' /></iq>"
        self.sock.send(client_message)
        logging.debug('Client:')
        logging.debug(client_message)

        server_response = self.sock.recv(BUFFER_SIZE)
        logging.debug('Server:')
        logging.debug(server_response)
        #print "received server_response:", server_response
        
        client_message = "<iq type='set' id='0'><session xmlns='urn:ietf:params:xml:ns:xmpp-session' /></iq>"
        
        self.sock.send(client_message)
        logging.debug('Client:')
        logging.debug(client_message)

        server_response = self.sock.recv(BUFFER_SIZE)
        #print "received server_response:", server_response
        
        client_message = "<presence xml:lang='en' />"
        
        self.sock.send(client_message)
        
        logging.debug('Client:')
        logging.debug(client_message)

        server_response = self.sock.recv(BUFFER_SIZE)
        logging.debug('Server:')
        logging.debug(server_response)
        #print "received server_response:", server_response
        
        userTmp = self.usrname
        client_message = "<iq from='" + self.usrname + "' id='bv1bs71f' type='get'> <query xmlns='jabber:iq:roster'/></iq>"
        self.sock.send(client_message)
        
        logging.debug('Client:')
        logging.debug(client_message)

        server_response = self.sock.recv(BUFFER_SIZE)
        print "received server_response:", server_response
        logging.debug('Server:')
        logging.debug(server_response)
        
        contact_list=[]
        full_xml=ET.fromstring(server_response)
        for node in full_xml.iter('{jabber:iq:roster}item'):
            jid = node.attrib.get('jid')
            contact_list.append(jid) 
        
        return contact_list 

    def click_list_item(self, event):
        list_widget = event.widget
        index = int(list_widget.curselection()[0])
        value = list_widget.get(index)
        #print value+"Selected"
        self.selFriend = value
        
        #send the message to the server 
    def send_msg(self,friend):
        print "sending to "+friend 
        writeMsg = self.writeMsgTexts[friend]
        contents = writeMsg.get(1.0, END)
        contents = contents.strip()
        #print('contents'+contents)
        conversation = self.conversationBoxes[friend]
        conversation.insert(END,self.usrname+":"+contents)
        self.writetosocket(self.selFriend,contents)

     #running in a thread,it waits for the message on the recv
    def readsocket(self, threadName, delay):
        while 1:
                        
            server_response = self.sock.recv(4096)
            logging.debug('Server:')
            logging.debug(server_response)
        
            #print "received"+server_response
            isbody=True
            full_xml = ET.fromstring(server_response)
            full_xml_root=full_xml.find(".")
            if full_xml_root.tag=="message":
                from_ = (full_xml_root.attrib)['from']
                from_ = re.match( r'([^/]*)/.*',from_, re.M|re.I)
                from_ = from_.group(1)

                try:
                    full_xml_root.iterfind("body").next()
                except StopIteration:
                    isbody=False
                        
                if isbody:
                    part_matched = re.match( r'^(<message)[^>]*><body>(.*)</body>.*',server_response, re.M|re.I)
                    recv_msg=part_matched.group(2)
                    #print (from_+" says : "+part_matched.group(2))
                    conversation = self.conversationBoxes[from_]
                    conversation.insert(END,from_+":"+recv_msg)
                    frame_ = self.createdframes[from_]
                    try:
                        istyping_ = self.typinglabels[from_]
                        istyping_["text"] = ""
                    except KeyError:  
                         pass 
                    
                    
                    
                    
                    
                elif full_xml_root.iterfind("composing"):
                    frame_ = self.createdframes[from_]
                    ifTyping = Label(frame_, text=str(from_)+" is typing..", font=("Helvetica", 8, "italic"))
                    ifTyping.grid(row=8, sticky=W)
                    ifTyping.config(state='active')
                    self.typinglabels[from_] = ifTyping
                    #print "typing notification received"
                    
            elif full_xml_root.tag=="presence":
                istype=True
                isstatus=True
                #print server_response
                from_ = (full_xml_root.attrib)['from']
                from__ = re.match( r'([^/]*)/.*',from_, re.M|re.I)
                if from__:
                    from_ = from__.group(1)
                try:
                    full_xml_root.iterfind("show").next()
                except StopIteration:
                    isstatus=False
                if  isstatus:
                    part_matched = re.match( r'^(<presence)[^>]*><show>(.*)</show>.*',server_response, re.M|re.I)
                    print (from_+" status is : "+part_matched.group(2))
                else:
                    try:
                        status_type=(full_xml_root.attrib)['type']
                    except KeyError:
                        istype=False
                            
                    if istype and status_type=="unavailable":
                        #print (from_+" is unavailable")
                        self.roster.itemconfig(self.contact_positions[from_], fg='red')
                    elif istype and status_type=="subscribe":
                        #print (from_+" wants to be a friend")
                        pass
                    else:
                        #print (from_+" is online")
                        #print ("Position is "+str(self.contact_positions[from_]))
                        self.roster.itemconfig(self.contact_positions[from_], fg='green')
    
    
    
    def writetosocket(self,to,msg):
        logging.debug('Client:')
        logging.debug(msg)

        self.sock.send("<message to='"+to+"' type='chat'><body>"+msg+"</body></message>")
        
    
    def afterSubmit(self):
        #print "Clicked!"
        #get authentication information
        authenticated = self.authFunc()
        if (authenticated):
            #retrieve the roster
            contacts = self.getroster()
            #create a new listener thread for recv
            try:               
               thread.start_new_thread(self.readsocket, ("Listener_thread", 2, ) )
               print "Created: readsocket"
            except:
               print "Error: unable to start thread"
            
            #print "contacts"
            #print contacts
            self.frame1.destroy()
            self.container.geometry('340x360')
            #print "Creating Menu"
            self.mBar = Menu(self.container)
            self.mBar.add_command(label="Add Contact", command=self.addContact)
            self.mBar.add_command(label="Logout", command=self.logOut)
            self.container.config(menu=self.mBar)
            #print "Creating Frame"
            self.frame2 = Frame(self.container)
            self.frame2.pack(fill=BOTH, expand=1)
            #print "Creating Label5"
            self.label5 = Label(self.frame2, text="Select friend from the roster and click on 'chat'")
            self.label5.grid(row = 0, column = 0, sticky=E+W+N+S)
            self.roster = Listbox(self.frame2, selectmode=EXTENDED)
            self.roster.bind('<<ListboxSelect>>', self.click_list_item)
            self.roster.grid(row=2, column = 0, columnspan=2, rowspan=3, sticky=E+W+N+S)
            
            i=0
            for user in contacts:
                self.contact_positions[user]=i
                i=i+1
                self.roster.insert(END, user)
            for key,value in self.contact_positions.iteritems():
                self.roster.itemconfig(value, fg='red')
                 
            print self.contact_positions    
            self.chat = Button(self.frame2, text="Chat", command=self.startChatting)
            self.chat.grid(row=9, column=0, columnspan=2, rowspan=1, sticky=E+W+S+N, padx=8, pady=27)        
        else:
            self.label4 = Label(self.frame1, text="User not authenticated! Try again.")
            self.label4.pack()
            
    def addContact(self):
        print "Adding contact"
        self.c = Toplevel(self.frame2)
        self.c.geometry('320x80')
        self.c.wm_title('Add Contact')
        self.frame4 = Frame(self.c)
        self.frame4.pack(fill=BOTH, expand=1)
        self.lbl = Label(self.frame4, text="Enter JID:")
        self.lbl.pack()
        self.addJID = Entry(self.frame4)
        self.addJID.pack()
        self.addButn = Button(self.frame4, text="Add", command=self.doneAdding)
        self.addButn.pack()
        
    
    def doneAdding(self):
        #Add functionality to add to roster here
        MESSAGE = "<presence type='subscribe' to='ritcson@is-a-furry.org' from='ritstudent@is-a-furry.org'/>"
        self.sock.send(MESSAGE)
        self.frame4.destroy()
        self.c.destroy()
        
    def logOut(self):
        print "Logging out"
        
    
    #method creates a new chat window
    def startChatting(self):
        print "Chatting.."
        self.chatwindow = Toplevel(self.frame2)
        self.chatwindow.geometry('355x380')
        self.chatwindow.wm_title(str(self.selFriend))
        frame3 = Frame(self.chatwindow)
        frame3.pack(fill=BOTH, expand=1)
        self.createdframes[self.selFriend]=frame3
        conversation = Listbox(frame3, selectmode=EXTENDED)
        conversation.grid(row=0, column=0, columnspan=3, rowspan=7, sticky=E+W+N,padx=20,pady=20)
        self.conversationBoxes[self.selFriend]=conversation
        writeMsg = Text(frame3, width=40, height=2)
        writeMsg.grid(sticky=S,padx=20,pady=20)
        self.writeMsgTexts[self.selFriend] = writeMsg
        #Add function to check if the selected friend is typing or not
        
        self.send = Button(frame3, text="Send",command= lambda: self.send_msg(self.selFriend))
        self.send.grid(row=9, column = 0)
    #handles authentication
    def authFunc(self):
        logging.debug('Beginning Auth')
        self.label6 = Label(self.frame1, text="Authenticating, please wait....")
        self.label6.pack()
                    
        usrname=self.id.get()
        psswrd=self.pswd.get()
        self.usrname=usrname
        self.passwd=psswrd
        #print "usrname: " + str(usrname)
        #print "psswrd: " + str(psswrd)
        matched_part = re.match( r'^([^@]*)@(.*)$', usrname, re.M|re.I)
        self.domain = matched_part.group(2)
        user_part =  matched_part.group(1)
        print user_part
        domain =self.domain 

        BUFFER_SIZE = 1024
        client_request = "<stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' to='"+domain+"' version='1.0'>"         
        logging.debug('Client:')
        logging.debug(client_request)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.connect(("is-a-furry.org",5222))
        self.sock.connect((domain,5222))
        self.sock.settimeout(None)
        
        self.sock.send(client_request)
        server_response = self.sock.recv(BUFFER_SIZE)
        logging.debug('Server:')
        logging.debug(server_response)
        
                  
        client_request = "<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'><required /></starttls>"
        self.sock.send(client_request)
        logging.debug('Client:')
        logging.debug(client_request)

        server_response = self.sock.recv(BUFFER_SIZE)        
        logging.debug('Server:')
        logging.debug(server_response)
        ssl_wrapper = ssl.wrap_socket(self.sock);
        self.sock=ssl_wrapper
        self.sock.do_handshake()
        
        
        client_request = "<stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' to='"+domain+"' version='1.0'>"
        
        self.sock.send(client_request)
        logging.debug('Client:')
        logging.debug(client_request)

        server_response = self.sock.recv(BUFFER_SIZE)
        #print "received server_response:", server_response
        logging.debug('Server:')
        logging.debug(server_response)
        
        encoded=base64.b64encode("\0"+user_part+"\0"+psswrd)
        client_request = "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>"+encoded+"</auth>"
        
        self.sock.send(client_request)
        logging.debug('Client:')
        logging.debug(client_request)

        server_response = self.sock.recv(BUFFER_SIZE)
        logging.debug('Server:')
        logging.debug(server_response)
        
        namespace="{urn:ietf:params:xml:ns:xmpp-sasl}"
        full_xml=ET.fromstring(server_response)
        for node in full_xml.iter():
            return (node.tag==namespace+"success")
        
def main():
    cli = Tk()
    cli.wm_title('XMPP Client')
    cli.geometry('480x320+30+30')
    pyCli = pyApp(cli)
    cli.mainloop()
    #cli.destroy()


if __name__ == '__main__':
    main() 