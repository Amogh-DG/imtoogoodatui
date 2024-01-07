import flet 
from flet import *
import mysql.connector as mysq
import random
import pyperclip
import time

db = mysq.connect(host = 'localhost', user = 'root', password = "amoghsql")
cursor = db.cursor(buffered=True)

#CREATING A DATABASE CALLED VAULTX ON MYSQL AND USING IT IN THE PROGRAM
cursor.execute("create database if not exists vaultx")
cursor.execute("use vaultx")
db.commit()

#OPENING A PAGE IN FULLSCREEN WITH VARIABLE NAME " page ", WITH THE TITLE OF THE PAGE BEING " VaultX "
def main(page :flet.Page):
    page.title = 'VaultX'
    page.window_full_screen = True

    # RAIL NAVIGATION IS USED TO SET BUTTON ACTIONS FOR THE VERTICAL INTERACTION BAR IN THE VAULT [ PRESENT IN LINE NO 440 ]
    def rail_navigation(e):
        if e.control.selected_index == 0:
            page.go('/vault')

        if e.control.selected_index == 1:
            page.go('/addentry')

        elif e.control.selected_index == 2:
            page.go('/editentry')

        elif e.control.selected_index == 3 :
            page.go('/deleteentry')

        elif e.control.selected_index == 4:
            page.go('/viewpasswords')                    

    #ROUTES THE PAGE DEPENDING ON WHAT THE ROUTE OF THE PAGE IS SET TO
    def reroute(e: RouteChangeEvent):
        page.views.clear()

        #CHECKING IF DATA ENTERED BY USER MEETS THE REQUIREMENTS OF THE PROGRAM
        def validate(e:ControlEvent):
            try:
                query='select username from login'
                cursor.execute(query)
                data=cursor.fetchall()
            except :
                data=[]

            if all([text_username.value,text_password.value]):  
                for i in range(0,len(data)):   
                    if text_username.value not in data[i]:                                      
                        text_username.error_text="User dosnt exit"
                        button_submit.disabled = True  

                    if text_username.value in data[i]:                                            
                        text_username.error_text=""                                            
                        button_submit.disabled = False
                        break
                    
            page.update()

        #WHEN DEF SUBMIT IS CALLED IT CHECKS WITH THE SQL DATABASE IF THE PASSWORD CORRESPONDING TO THE ENTERED USERNAME IS CORRECT AND PUSHES THE USER TO THE HOMEPAGE    
        #OTHERWISE A DIALOGUE BOX IS DISPLAYED   
        def submit(e: ControlEvent):
            username=text_username.value
            password=text_password.value
            cursor.execute("select * from login")
            data =  cursor.fetchall()
            for i in data:
                if i == (username,password):
                    global loginn
                    loginn=username
                    page.clean()
                    page.go('/homepage')
                    break
            
            else:
                page.dialog = dlg = flet.AlertDialog(title=flet.Text("Incorrect Password"))
                dlg.open = True
                page.update()

        #CONTENTS OF THE UI ON THE PAGE IS SET TO A VARIABLE BEFORE ITS BEING PLACED ONTO VIEW WHICH APPENDS IT ONTO THE PAGE WHEN CALLED
        appbar : AppBar = AppBar(title=Text("VaultX"),bgcolor='blue')
        text_login: Text = Text('VaultX Login',text_align=flet.TextAlign.CENTER,size=30)
        text_username: TextField = TextField(label='Username',text_align=flet.TextAlign.LEFT,width=300)
        text_password: TextField = TextField(label='Password',text_align=flet.TextAlign.LEFT,password=True,can_reveal_password=True,width=300)
        button_submit: ElevatedButton = ElevatedButton(text='Sign in',width=300,disabled=True)
        button_signup: ElevatedButton = ElevatedButton(text='Sign up',width=300,on_click=lambda _:page.go('/registration'))

        #TEXTFIELD ACTIONS
        text_username.on_change = validate
        text_password.on_change = validate 

        #BUTTON ACTIONS
        button_submit.on_click = submit

        #UI FIELD PLACEMENTS FOR MAIN PAGE
        page.views.append(
            View(
                route='/',
                controls=[text_login,
                          appbar,
                          text_username,
                          text_password,
                          button_submit,
                          button_signup
                          ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER
            )
        )

        #CHECKING WHICH VIEW TO APPEND DEPENDING ON PAGE.ROUTE VARIABLE
        if page.route == '/registration':
            
            #CHECKING IF THE ENTERERD DATA MEETS THE REQUIREMENTS OF THE PROGRAM
            def register(e:ControlEvent):
                username=reg_username.value
                password=reg_password.value
                confpass=reg_confirm.value

                if username == password:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Username and Password cannot be the same"))
                    dlg.open = True
                    page.update()
                
                elif ' ' in username:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Username cannot contain spaces"))
                    dlg.open = True
                    page.update()

                elif ' ' in password:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Password cannot contain spaces"))
                    dlg.open = True
                    page.update()

                elif password == confpass:
                    cursor.execute("create table if not exists login(username varchar(30), password varchar(30))")
                    insert_query="insert into login values('%s','%s')"
                    insert_para=(username,password)
                    cursor.execute(insert_query % insert_para)
                    db.commit()
                    page.go('/')

            #UI CONTROLEVENT TO CHECK CURRENT CONDITIONS OF GIVEN VALUE
            def validate_reg(e:ControlEvent):
                
                #TRYING TO LOAD USERNAMES FROM TABLE TABLE LOGIN IF IT EXISTS
                try:
                    cursor.execute('select username from login')
                    data =  cursor.fetchall()
                    registered_users = [i[0] for i in data]
                except:
                    registered_users=[]

                #CHECKING IF DATA MEETS THE REQUIREMENTS TO REGISTER
                if all([reg_username.value,reg_password.value,reg_confirm.value]):

                    if reg_username.value in registered_users:
                        reg_username.error_text="User already exists"
                        reg_submit.disabled = True

                    if reg_username.value not in registered_users:
                        reg_username.error_text = ""
                        reg_submit.disabled = False

                    if all([reg_password.value != reg_confirm.value]):
                        reg_confirm.error_text="These Passwords didnt match. Try again"
                        reg_submit.disabled = True

                    if all([reg_password.value == reg_confirm.value]):
                        reg_confirm.error_text=""

                    if all([reg_password.value == reg_confirm.value]) and reg_username.value not in registered_users:
                        reg_submit.disabled = False

                    page.update()

            #UI APPBAR,BUTTONS AND TEXTFIELDS CREATION FOR REGISTRATION PAGE
            reg_appbar : AppBar =  AppBar(title=Text("Registration"),bgcolor='blue')
            reg_text : Text = Text("Create a VaultX User",size=25)
            reg_username: TextField = TextField(label='Username',text_align=flet.TextAlign.LEFT,width=300)
            reg_password: TextField = TextField(label='Password',text_align=flet.TextAlign.LEFT,password=True,can_reveal_password=True,width=300)
            reg_confirm: TextField = TextField(label='Confirm Password',text_align=flet.TextAlign.LEFT,password=True,can_reveal_password=True,width=300)
            reg_submit: ElevatedButton = ElevatedButton(text='Sign up',width=300,disabled=True)

            #UI FIELD PLACEMENTS FOR REGISTRATION PAGE
            page.views.append(
            View(
                route='/registration',
                controls=[reg_appbar,
                          reg_text,
                          reg_username,
                          reg_password,
                          reg_confirm,
                          reg_submit],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )
            #TEXTFIELD ACTIONS
            reg_username.on_change = validate_reg
            reg_password.on_change = validate_reg
            reg_confirm.on_change = validate_reg

            #BUTTON ACTION
            reg_submit.on_click = register

        elif page.route == '/homepage':

            #UI APPBAR,BUTTONS AND TEXTFIELD CREATION FOR HOMEPAGE
            home_appbar : AppBar = AppBar(title=Text("HomePage"),bgcolor='blue')
            text_vaultx: Text = Text("VaultX",size=50)
            text_quote: Text = Text("Store your passwords in a secure vaultx database",size=20)
            button_createvault : ElevatedButton = ElevatedButton(text="Create Vault",width=460,on_click=lambda _:page.go('/createvault'))
            button_openvault : ElevatedButton = ElevatedButton(text="Access Vault",width=460,on_click=lambda _:page.go('/accessvault'))
            button_randompassgen : ElevatedButton = ElevatedButton(text="Strong Password Generator",width=460,on_click=lambda _:page.go('/passgen'))

            #UI FIELD PLACEMENTS FOR HOMEPAGE
            page.views.append(
            View(
                route='/homepage',
                controls=[
                          home_appbar,
                          text_vaultx,
                          text_quote,
                          button_createvault,
                          button_openvault,
                          button_randompassgen
                          ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )
            
        elif page.route == '/createvault':

            #CHECKING IF DATA MEETS REQUIREMENTS TO CREATE A VAULT
            def validate_new(e:ControlEvent):
                cursor.execute("create table if not exists vault_auth(login varchar(50), username varchar(50), password varchar(20))")
                cursor.execute("select username from vault_auth")
                data_allusers = cursor.fetchall()
                vaults = [i[0] for i in data_allusers]

                if all([vname.value,vpassword.value,vconfirm.value]):

                    if vpassword.value != vconfirm.value:
                        vconfirm.error_text="Passwords dont match"
                        cvaultbutton.disabled = True

                    if vname.value in vaults:
                        vname.error_text = "Vault name in use"
                        cvaultbutton.disabled = True

                    if vname.value not in vaults:
                        vname.error_text = ""
                    
                    if vpassword.value == vconfirm.value:
                        vconfirm.error_text = ""

                    if vpassword.value == vconfirm.value and vname.value not in vaults:
                        cvaultbutton.disabled = False

                else:
                    cvaultbutton.disabled = True

                page.update()

            #SQL LOGIC FOR CREATING A VAULT
            def vault_create(e:ControlEvent):
                vault_username=vname.value
                vault_password=vpassword.value
                confirm_password=vconfirm.value

                if vault_password == confirm_password:
                    query = "insert into vault_auth values(%s,%s,%s)"  
                    para = (loginn,vault_username,confirm_password)
                    cursor.execute(query,para)
                    query_create="create table %s(title varchar(40),username varchar(40),password varchar(80),url varchar(200), notes varchar(40))"
                    para_create = vault_username
                    cursor.execute(query_create % (para_create,))
                    db.commit()
                    page.go('/accessvault')

            #UI APPBAR,BUTTONS AND TEXTFIELD CREATION FOR CREATE VAULT PAGE
            nv_text : Text = Text(value='Create New Vault',size=30)
            nv_appbar : AppBar = AppBar(title=Text("Vault Creation"),bgcolor='blue')
            vname :TextField = TextField(label="Enter Vault Name",text_align=MainAxisAlignment.CENTER,width=300,on_change=validate_new)
            vpassword :TextField = TextField(label="Enter Vault password",text_align=MainAxisAlignment.CENTER,width=300,password=True,can_reveal_password=True,on_change=validate_new)
            vconfirm: TextField = TextField(label="Confirm Vault password",text_align=MainAxisAlignment.CENTER,width=300,password=True,can_reveal_password=True,on_change=validate_new)
            cvaultbutton : ElevatedButton = ElevatedButton(text='Create Vault',width=300,on_click=vault_create,disabled=True)

            #UI FIELD PLACEMENTS FOR VAULT CREATION PAGE
            page.views.append(
            View(
                route='/createvault',
                controls=[
                nv_appbar,
                nv_text,
                vname,
                vpassword,
                vconfirm,
                cvaultbutton
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER
            )
        )

        elif page.route == '/accessvault':
            
            #CHECKING IF ALL THE FIELDS ARE FILLED IN TO ENABLE THE " ACCESS VAULT " BUTTON
            def validate_access(e:ControlEvent):
                if all([accessvault_vname.value,accessvault_vpass.value]):
                        accessv_button.disabled = False
                else:
                    accessv_button.disabled = True
                page.update()

            #ON CLICK FUNCTION DEFINION FOR BUTTON " CREATE VAULT " WHICH CHECKS IF PASSWORD ENTERED CORRESPONDS WITH ENTERED USERNAME USING SQL
            def func_buttonaccess(e:ControlEvent):
                vault_username=accessvault_vname.value
                vault_password=accessvault_vpass.value
                
                try:
                    cursor.execute("select login, username, password from vault_auth")
                    data = cursor.fetchall()
                except:
                    dont_exist = flet.AlertDialog(title=flet.Text("Please Create a Vault!"))
                    page.dialog = dont_exist
                    dont_exist.open = True
                    page.update()
                    page.go('/createvault')
                
                for i in data:
                    if i == (loginn,vault_username,vault_password):
                        global whichvault
                        whichvault=vault_username
                        page.go('/vault')
                        break

                else:
                    wrong_password = flet.AlertDialog(title=flet.Text("Incorrect Login Credentials! Try again"))
                    page.dialog = wrong_password
                    wrong_password.open = True
                    page.update()

            #UI APPBAR, BUTTONS AND TEXTFIELD CREATION FOR ACCESS VAULT PAGE
            accessvault_txt :Text = Text(value='Access Vault',size=30)
            accessvault_appbar :AppBar = AppBar(title=Text("Access Vault"),bgcolor='blue')
            accessvault_vname:TextField = TextField(label="Enter Vault Name",text_align=MainAxisAlignment.CENTER,width=300,on_change=validate_access)
            accessvault_vpass:TextField = TextField(label="Enter Vault password",text_align=MainAxisAlignment.CENTER,width=300,password=True,can_reveal_password=True,on_change=validate_access)
            accessv_button: ElevatedButton = ElevatedButton(text='Access Vault',width=300,on_click=func_buttonaccess,disabled=True)

            #UI FIELD PLACEMENT FOR ACCESS VAULT PAGE
            page.views.append(
            View(
                route='/accessvault',
                controls=[
                accessvault_appbar,
                accessvault_txt,
                accessvault_vname,
                accessvault_vpass,
                accessv_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER
            )
        )
            
        elif page.route == '/passgen':
            
            #LOGIC FOR GENERATING A STRONG RANDOM PASSWORD
            def passgen_logic(e):
                    alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                    numbers = ['1','2','3','4','5','6','7','8','9','0']
                    special = ['@','!','#','$','%','&']
                    randompass = ""
                    mainlist = [alphabets,numbers,special]
                    lenofpass = random.randint(12,16)
                    for i in range(lenofpass):
                        listpicker = random.randint(0,2)
                        if listpicker == 0:
                            elementpicker = random.randint(0,25)
                            randompass += alphabets[elementpicker]
                        elif listpicker == 1:
                            elementpicker = random.randint(0,9)
                            randompass += numbers[elementpicker]
                        else:
                            elementpicker = random.randint(0,5)
                            randompass += special[elementpicker]

                    def close_dlg(e):
                        passdisplay.open = False
                        page.update()

                    def yes(e):
                        pyperclip.copy(randompass)
                        passdisplay.open = False
                        page.update()

                    passdisplay = flet.AlertDialog(
                        modal=True,
                        title=flet.Text("Generated Strong Password: {}".format(randompass)),
                        content=flet.Text("Do you want to copy the generated password to clipboard?"),
                        actions=[
                            flet.TextButton("Yes", on_click=yes),
                            flet.TextButton("No", on_click=close_dlg),],
                        actions_alignment=flet.MainAxisAlignment.END)

                    page.dialog = passdisplay
                    passdisplay.open = True
                    page.update()

            #UI APPBAR, BUTTONS AND TEXTFIELD CREATION FOR ACCESS VAULT PAGE
            passgen_text: Text = Text(value='Password Genarator',size=30)
            passgen_appbar: AppBar = AppBar(title=Text("Password Genarator"),bgcolor='blue')
            genpassword_button : ElevatedButton = ElevatedButton(text="Generate Strong Password",width=250,on_click=passgen_logic)

            #UI FIELD PLACEMENT FOR PASSGEN PAGE
            page.views.append(
            View(
                route='/passgen',
                controls=[
                    passgen_appbar,
                    passgen_text,
                    genpassword_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER
            )
        )
            
        elif page.route == '/vault':

            #CREATION OF SIDEBAR COMPONENT ( RAIL ) IN VAULT PAGE
            rail = flet.NavigationRail(
                label_type=flet.NavigationRailLabelType.ALL,
                min_width=100,
                min_extended_width=400,
                height=920,
                selected_index=0,
                destinations=[
                    flet.NavigationRailDestination(
                        icon=icons.HOME, selected_icon=icons.HOME_FILLED, label="Home"
                    ),
                    flet.NavigationRailDestination(
                        icon=icons.ADD, selected_icon=icons.ADD_ROUNDED, label="Add"
                    ),
                    flet.NavigationRailDestination(
                        icon=icons.EDIT_OUTLINED,selected_icon=icons.EDIT_ROUNDED,
                        label="Edit"
                    ),
                    flet.NavigationRailDestination(
                        icon=icons.DELETE_OUTLINE_ROUNDED,selected_icon=icons.DELETE_ROUNDED,
                        label_content=flet.Text("Delete"),
                    ),
                    flet.NavigationRailDestination(
                        icon=icons.PASSWORD_OUTLINED,selected_icon=icons.PADDING_ROUNDED,
                        label_content=flet.Text("View Pass"),
                    )
                ],
                on_change=rail_navigation,
            )

            #LOADING DATA FROM SQL AND INSERTING IT AS A ROW INTO THE UI TABLE
            def load_data():
                query="select title,username,url,notes from %s"
                para = whichvault
                cursor.execute(query % (para,))
                data = cursor.fetchall()
                
                for i in range(len(data)):
                    Table.rows.append(
                        DataRow(
                            cells=[DataCell(Text("{}".format(data[i][0]))),
                                   DataCell(Text("{}".format(data[i][1]))),
                                   DataCell(Text("{}".format(data[i][2]))),
                                   DataCell(Text("{}".format(data[i][3])))] 

                        )
                    )
                page.update()

            gap = flet.Text("")
            
            #CREATION OF TABLE COMPONENT IN VAULT PAGE
            Table = DataTable(border=flet.border.all(0, "white"),
                              horizontal_lines=flet.border.BorderSide(0, "white"),
                              vertical_lines=flet.border.BorderSide(0,"white"),
                              width=1669,
                              height=930,
                              show_bottom_border=True,
                              show_checkbox_column=True,
                              columns=[flet.DataColumn(flet.Text("Title")),
                                      flet.DataColumn(flet.Text("Username")),
                                      flet.DataColumn(flet.Text("URL")),
                                      flet.DataColumn(flet.Text("Notes"))],
                                      rows=[],)
            
            load_data()

            #CREATION OF UI COMPONENTS FOR VAULT PAGE
            vault_appbar :AppBar = AppBar(title=Text("Password Vault"),bgcolor='blue')
            smallgap_text : Text = Text("    ")
            gap_text : Text = Text("            ")

            #UI FIELD PLACEMENT FOR ACCESS VAULT PAGE
            page.views.append(
                View(
                    route='/vault',
                    controls=[gap_text,
                        Row(
                            [smallgap_text,
                                Column(
                                    [
                                    rail
                                    ],
                                    spacing = 15,
                                ),
                            gap_text,Table]
                        ),
                        vault_appbar,
                        gap]
                )
            )

        elif page.route=='/addentry':
            
            #SQL LOGIC TO ADD AN ENTRY TO VAULT TABLE [ SQL TABLE NAMES FOR VAULTS WILL DIFFER ]
            def entry_to_sql(e):
                try:
                    fetch_query = "select title from %s"
                    cursor.execute(fetch_query % whichvault)
                    fetch_data= cursor.fetchall()
                    fetch_data = [i[0] for i in fetch_data]
                except:
                    fetch_data=[]

                title_entry=title.value 
                username_entry=username.value
                password_entry=password.value
                url_entry=url.value
                notes_entry=notes.value
                user = whichvault

                if title_entry not in fetch_data:
                    query="insert into %s values('%s','%s','%s','%s','%s')"
                    para=(user,title_entry,username_entry,password_entry,url_entry,notes_entry)
                    cursor.execute(query % para)
                    db.commit()
                    page.go('/vault')

                elif title_entry in fetch_data:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Title already exists! Choose another Title"))
                    dlg.open = True
                    page.update()

            #CREATION OF UI COMPONENTS FOR ADDENTRY PAGE
            addentry_appbar: AppBar = AppBar(title=Text("Add Entry"),bgcolor='blue')
            addentry_text : Text = Text('ADD ENTRY',size=30)
            title : TextField = TextField(label="Title",width=400)
            username : TextField = TextField(label="Username",width=400)
            password : TextField = TextField(label="Password",width=400,password=True,can_reveal_password=True)
            url : TextField = TextField(label="URL",width=400)
            notes : TextField = TextField(label="Notes",width=400)
            add_button : ElevatedButton = ElevatedButton(text="ADD PASSWORD ENTRY",width=400,on_click=entry_to_sql)  

            #PLACEMENT OF UI COMPONENTS IN ADDENTRY PAGE
            page.views.append(
            View(
                route='/addentry',
                controls=[
                    addentry_appbar,
                    addentry_text,
                    title,
                    username,
                    password,
                    url,
                    notes,
                    add_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )
        
        elif page.route=='/editentry':
            
            #SQL LOGIC TO EDIT ENTRIES GIVEN IN VAULT [ SQL TABLE NAMES FOR VAULTS WILL DIFFER ]
            def edit_to_sql(e):
                title_toedit = prev_title.value
                new_title=edit_title.value
                new_username=edit_username.value
                new_password=edit_password.value
                new_url=edit_url.value
                new_notes=edit_notes.value
                
                try:
                    fetch_query = "select title from %s"
                    cursor.execute(fetch_query % whichvault)
                    fetch_data= cursor.fetchall()
                    title_data = [i[0] for i in fetch_data]
                except:
                    title_data=[]

                if title_toedit in title_data:
                    query = " update %s set title='%s',username='%s',password='%s',url='%s',notes='%s' where title='%s' "
                    para = (whichvault,new_title,new_username,new_password,new_url,new_notes,title_toedit)
                    cursor.execute(query % para)
                    db.commit()
                    page.go('/vault')

                elif title_toedit not in title_data:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Title Entry does not exist"))
                    dlg.open = True
                    page.update()

            #CREATION OF UI COMPONENTS FOR EDIT ENTRY PAGE
            editentry_appbar: AppBar = AppBar(title=Text("Edit Entry"),bgcolor='blue')
            editentry_text : Text = Text('Edit Entry',size=30)
            information_text : Text = Text('Enter the title name of the entry to change',size=15)
            prev_title : TextField = TextField(label="Existing title ",width=400)
            bottom_information_text : Text = Text('Enter new details',size=20)
            text_gap : Text = Text("")
            edit_title : TextField = TextField(label="New Title",width=400)
            edit_username : TextField = TextField(label="New Username",width=400)
            edit_password : TextField = TextField(label="New Password",width=400,password=True,can_reveal_password=True)
            edit_url : TextField = TextField(label="New URL",width=400)
            edit_notes : TextField = TextField(label="New Notes",width=400)
            edit_button : ElevatedButton = ElevatedButton(text="EDIT ENTRY",width=400,on_click=edit_to_sql)   

            #PLACEMENT OF UI COMPONENETS FOR EDIT ENTRY PAGE
            page.views.append(
            View(
                route='/editentry',
                controls=[
                    editentry_appbar,
                    editentry_text,
                    information_text,
                    prev_title,
                    text_gap,
                    bottom_information_text,
                    edit_title,
                    edit_username,
                    edit_password,
                    edit_url,
                    edit_notes,
                    edit_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )

        elif page.route == '/deleteentry':
            #SQL LOGIC TO DELETE ENTRY IN VAULT TABLE [ SQL TABLE NAMES FOR VAULTS WILL DIFFER ]
            def delete_in_sql(e):
                title_todelete = delete_title.value
                confirmpass_todelete = delete_passconfirm.value

                conf_query = "select password from vault_auth where username='%s' "
                cursor.execute(conf_query % whichvault)
                conf = cursor.fetchall()
                password = [i[0] for i in conf]

                try:
                    fetch_query = "select title from %s"
                    cursor.execute(fetch_query % whichvault)
                    fetch_data= cursor.fetchall()
                    title_data = [i[0] for i in fetch_data]

                except:
                    title_data=[]

                if title_todelete in title_data:

                    if confirmpass_todelete in password:
                        query = " delete from %s where title='%s' "
                        para = (whichvault , title_todelete)
                        cursor.execute(query % para)
                        db.commit()
                        page.go('/vault')

                    elif confirmpass_todelete not in password:
                        page.dialog = dlg = flet.AlertDialog(title=flet.Text("Vault password is incorrect! Try again"))
                        dlg.open = True
                        page.update()

                elif title_todelete not in title_data:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Title Entry does not exist"))
                    dlg.open = True
                    page.update()

            #CREATION OF UI COMPONENTS FOR ADD ENTRY PAGE
            deleteentry_appbar: AppBar = AppBar(title=Text("Delete Entry"),bgcolor='blue')
            deleteentry_text : Text = Text('Delete Entry',size=30)
            information_text : Text = Text('Enter the title name of the entry to delete',size=15)
            delete_title : TextField = TextField(label="Existing title ",width=400)
            bottom_information_text : Text = Text('Confirm Vault Password',size=20)
            delete_passconfirm : TextField = TextField(label="Confirm Vault Password",width=400,password=True,can_reveal_password=True)
            text_gap : Text = Text("")
            delete_button : ElevatedButton = ElevatedButton(text="DELETE ENTRY",width=400,on_click=delete_in_sql)  

            #PLACEMENT OF UI COMPONENETS FOR ADD ENTRY PAGE
            page.views.append(
            View(
                route='/deleteentry',
                controls=[
                    deleteentry_appbar,
                    deleteentry_text,
                    information_text,
                    delete_title,
                    text_gap,
                    bottom_information_text,
                    delete_passconfirm,
                    delete_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )
            
        elif page.route == '/viewpasswords':
            #SQL LOGIC TO LOAD DATA FROM VAULT TABLE AND DISPLAY PASSWORD ACCORDING TO TITLE NAME PROVIDED [ SQL TABLE NAMES FOR VAULTS WILL DIFFER ]
            def view_from_sql(e):
                title_toview = view_title.value
                confirmpass_toview = view_passconfirm.value

                conf_query = "select password from vault_auth where username='%s' "
                cursor.execute(conf_query % whichvault)
                conf = cursor.fetchall()
                password = [i[0] for i in conf]

                titleconf_query = "select title from %s"
                cursor.execute(titleconf_query % whichvault)
                existingtitle_nested = cursor.fetchall()
                existingtitles = [i[0] for i in existingtitle_nested]

                #CHECKING IF ENTERED TITLE [ TITLE TO VIEW ] IS AN EXISTING TITLE [ EXISTING TITLES IS A LIST OF TITLES PRESENT IN THE CURRENT VAULT]
                if title_toview in existingtitles:

                    if confirmpass_toview in password:
                        query = " select password from %s where title='%s' "
                        para = (whichvault , title_toview)
                        cursor.execute(query % para)
                        fetchall_password_data =  cursor.fetchall()
                        password_data = [i[0] for i in fetchall_password_data]

                        def close_dlg(e):
                            passdisplay.open = False
                            page.update()
                            page.go('/vault')

                        def yes(e):
                            pyperclip.copy(password_data[0])
                            passdisplay.open = False
                            page.update()
                            page.go('/vault')

                        passdisplay = flet.AlertDialog(
                            modal=True,
                            title=flet.Text("The password for title {} : {}".format(title_toview,password_data[0])),
                            content=flet.Text("Do you want to copy the password to clipboard?"),
                            actions=[
                                flet.TextButton("Yes", on_click=yes),
                                flet.TextButton("No", on_click=close_dlg),],
                            actions_alignment=flet.MainAxisAlignment.END)

                        page.dialog = passdisplay
                        passdisplay.open = True
                        page.update()

                    elif confirmpass_toview not in password:
                        page.dialog = dlg = flet.AlertDialog(title=flet.Text("Vault password is incorrect! Try again"))
                        dlg.open = True
                        page.update()
                
                elif title_toview not in existingtitles:
                    page.dialog = dlg = flet.AlertDialog(title=flet.Text("Password entry with Title {} dosnt exist".format(title_toview)))
                    dlg.open = True
                    page.update()

            #CREATION OF UI COMPONENETS FOR PAGE VIEW ENTRY
            viewentry_appbar : AppBar = AppBar(title=Text("View passwords"),bgcolor='blue')
            viewentry_text : Text = Text('View Passwords',size=30)
            information_textview : Text = Text('Enter title of password entry to view',size=15)
            view_title : TextField = TextField(label="Existing title ",width=400)
            bottom_information_text_view : Text = Text('Confirm Vault Password',size=20)
            view_passconfirm : TextField = TextField(label="Confirm Vault Password",width=400,password=True,can_reveal_password=True)
            text_gap : Text = Text("")
            view_button : ElevatedButton = ElevatedButton(text="VIEW PASSWORD",width=400,on_click=view_from_sql)    

            #PLACEMENT OF UI COMPONENETS FOR PAGE VIEW ENTRY
            page.views.append(
            View(
                route='/viewpasswords',
                controls=[
                    viewentry_appbar,
                    viewentry_text,
                    information_textview,
                    view_title,
                    text_gap,
                    bottom_information_text_view,
                    view_passconfirm,
                    view_button
                ],
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            )
        )

    #PAGE.UPDATE() RUNS AFTER EVERY ROUTE CHANGE OCCURS TO SAVE CHANGES TO THE PAGE THAT HAVE BEEN MADE
    page.update()

    #TAKES CARE OF THE NAVIGATION ON THE BACK ARROW PRESENT ON APPBAR
    def view_pop(e: ViewPopEvent):
        page.views.pop()
        if page.route == '/addentry' or page.route == '/editentry' or page.route == '/deleteentry' or page.route == '/viewpasswords':
            page.go('/vault')
        elif page.route == '/homepage' or page.route == '/registration':
            top_view : View = page.views[-1]
            page.go(top_view.route)
        elif page.route == '/createvault' or '/accessvault' or '/passgen':
            page.go('/homepage')
            
    #DEFINION CALLS ACTION
    page.on_route_change = reroute
    page.on_view_pop = view_pop
    page.go(page.route)

#PAGE LOOP
flet.app(target=main)
