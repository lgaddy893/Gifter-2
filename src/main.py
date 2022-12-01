
from msilib.schema import ProgId
from multiprocessing.sharedctypes import Value
import streamlit as st
import pandas as pd
from account import Account
from account_info import AccountInfo
from item import item
from datetime import datetime
import re

email_sent = False

def initial_page():
    st.header("Gift Finder!")
    create = st.button('Create Account') 
    login = st.button('Log In')
    if create:
        st.session_state.runpage = 'createaccount'
        st.experimental_rerun()
    if login:
        st.session_state.runpage = 'login'
        st.experimental_rerun()

def login_page():
    form1 = st.form(key='Login form')
    f_name = form1.text_input('User Name')
    password = form1.text_input('Enter a password', type='password')
    but = form1.form_submit_button('Log in')
    if but:
        accountMan = AccountInfo()
        info = accountMan.get_account(f_name,password)
        if isinstance(info, int) == True and info == -2:
            st.error("Password is wrong. Please put valid password!")
            st.session_state.runpage = 'login'
        elif isinstance(info, int) == True and info == -1:
            st.error("User Name is Incorrect. Please use correct user name!")
            st.session_state.runpage = 'login'
        else:
            acc = Account(ID = info[0],username = f_name,password = password)
            st.session_state.runpage = 'account'
            st.session_state.account = acc
            st.experimental_rerun()
            
    if st.button('Back'):
        st.session_state.runpage = 'initial'
        st.experimental_rerun() 
    
def create_account():
    st.write('Please fill out the form')
    form = st.form(key='Create_form')
    f_name = form.text_input('First Name:')
    surname = form.text_input('Last Name:')
    birthday = form.text_input('Birthday (MM/DD/YYYY):')
    email = form.text_input('Email:')
    notifications = form.text_input('Email notifications (enter On or Off):')
    username = form.text_input('User Name:')
    password = form.text_input('Enter a password:', type='password')
    interest = form.text_input('Interests (please enter them comma seperated):')
    but1 = form.form_submit_button('Submit')

    # check if birthday is valid format
    format = "%m/%d/%Y"
    validB = True
    try:
        validB = bool(datetime.strptime(birthday, format))
    except ValueError:
        validB = False

    # check if email is valid format using regex
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    validE = True
    if not (re.fullmatch(regex, email)):
        validE = False
    
    # when create account button is clicked, check input before creating account
    if but1:
        error = False
        errorMessage = ""
        if (f_name == ""):
            error = True
            errorMessage += "Name cannot be empty.\n"
        if (surname == ""):
            error = True
            errorMessage += "Surname cannot be empty.\n"
        if (birthday == "" or validB == False):
            error = True
            errorMessage += "Birthday should be formatted MM/DD/YYYY.\n"
        if (email == "" or validE == False):
            error = True
            errorMessage += "Please enter a valid email.\n"
        if (notifications == "" or notifications != "On"):
            if (notifications != "Off"):
                error = True
                errorMessage += "Email notifications should be either 'On' or 'Off'.\n"
        # if there is an error, print the associated messages and allow for user to correct
        if (error == True):
            st.error(errorMessage)
        # if there is not an error, create the account
        acc = Account(f_name, surname, birthday, email, notifications, username, password, interest)
        if int(acc.ID)==-2:
            st.session_state.runpage = 'createaccount'
            # st.write('Please fill out the form with unique user name')
            # st.experimental_rerun()
        else:
            Account(ID = int(acc.ID))
            st.session_state.runpage = 'account'
            st.session_state.account = acc
            st.experimental_rerun()
    #return account
    
    if st.button('Back'):
        st.session_state.runpage = 'initial'
        st.experimental_rerun() 

def account_page():
    acc = st.session_state.account
    st.header('Welcome ' + acc.name + '!')
    st.write("What a beautiful day to gift!")
    if st.button('Profile'):
        st.session_state.runpage = 'profile'
        st.experimental_rerun()
    if st.button('Wishlist'): 
        st.session_state.runpage = 'wishlist'
        st.experimental_rerun()
    if st.button('Friendlist'):
        st.session_state.runpage = 'friendlist'
        st.experimental_rerun()
    if st.button('Logout'):
        st.session_state.runpage = 'initial'
        st.experimental_rerun()
    # check if whether a notification email needs to be sent today (is it 1 week before the account's birthday)
    global email_sent

    birthday = acc.birthday
    b = birthday.rpartition('/')[0] + birthday.rpartition('/')[1]
    b = b[:-1]
    month = b.rpartition('/')[0]
    day = b.rpartition('/')[2]
    currDate = datetime.now().date()

    birthdayDate = str(month) + "/" + str(day)

    if (int(currDate.month) > int(month) and int(currDate.day) > int(day)):
        birthdayDate += "/" + str(currDate.year + 1)
    else:
        birthdayDate += "/" + str(currDate.year)
        
    birthdayDate = datetime.strptime(birthdayDate, "%m/%d/%Y").date()

    if (birthdayDate - currDate).days == 7 and email_sent == False:
            email_sent = True
            if (acc.friendlist != 'NaN' and acc.wishlist != 'NaN'):
                acc.send_reminder_email()
                acc = Account(ID = int(acc.ID))
                st.session_state.account = acc
                st.session_state.runpage = 'profile'
            else:
                st.error("Please ensure you have added items to your wishlist and friends to your friendlist before attempting to send email notifications.")
            st.experimental_rerun()
    else:
        email_sent = False

def profile_page():
    st.header('Profile')
    acc = st.session_state.account
    st.write('ID: ' + str(acc.ID))
    st.write('First Name: ' + acc.name)
    st.write('Last Name: ' + acc.surname)
    st.write('Birthday: ' + acc.birthday)
    st.write('User Name: ' + acc.username)
    st.write('Password: ' + acc.password)
    st.write('Email: ' + acc.email)
    st.write('Email Notifications: ' + acc.notifications)
    st.write('Interests: ' + (acc.interests).replace("\"", ""))
    if st.button("Edit Profile"):
        st.session_state.runpage = 'editprofile'
        st.experimental_rerun()
    if st.button("Back"):
        st.session_state.runpage = 'account'
        st.experimental_rerun()
    if st.button("Send Notifications"):
        if (acc.friendlist != 'NaN' and acc.wishlist != 'NaN'):
            acc.send_reminder_email()
        else:
            st.error("Please ensure you have added items to your wishlist and friends to your friendlist before attempting to send email notifications.")
        st.experimental_rerun()

def editprofile_page():
    st.header('Edit Profile')
    form = st.form(key='EditProfileForm')
    acc = st.session_state.account
    name = form.text_input('First Name:', value= acc.name, placeholder= acc.name)
    surname = form.text_input('Last Name:', value= acc.surname, placeholder= acc.surname)
    birthday = form.text_input('Birthday:', value= acc.birthday, placeholder= acc.birthday)
    email = form.text_input('Email:', value= acc.email, placeholder= acc.email)
    notifications = form.text_input('Email Notifications:', value= acc.notifications, placeholder= acc.notifications)
    username = form.text_input('User Name:', value= acc.username, placeholder= acc.username)
    password = form.text_input('Password:', value= acc.password, placeholder= acc.password)
    ints = (acc.interests).replace("\"", "")
    interests = form.text_input('Interest:', value=ints, placeholder=ints)
    
    case = -1
    chars = set("~!@#$%^&*()_+=")
    if form.form_submit_button('Update'):
        # check if birthday is valid format
        format = "%m/%d/%Y"
        validB = True
        try:
            validB = bool(datetime.strptime(birthday, format))
        except ValueError:
            validB = False

        # check if email is valid format using regex
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        validE = True
        if not (re.fullmatch(regex, email)):
            validE = False
        
        error = False
        errorMessage = ""
        if (name == ""):
            error = True
            errorMessage += "Name cannot be empty.\n"
        if (surname == ""):
            error = True
            errorMessage += "Surname cannot be empty.\n"
        if (birthday == "" or validB == False):
            error = True
            errorMessage += "Birthday should be formatted MM/DD/YYYY.\n"
        if (email == "" or validE == False):
            error = True
            errorMessage += "Please enter a valid email.\n"
        if (notifications == "" or notifications != "On"):
            if (notifications != "Off"):
                error = True
                errorMessage += "Email notifications should be either 'On' or 'Off'.\n"
        # if there is an error, print the associated messages and allow for user to correct
        if (error == True):
            st.error(errorMessage)
        # if there is not an error, update the account
        else:   
            acc.update_account(name, surname, birthday, email, notifications, username, password,interests)
            acc = Account(ID = int(acc.ID))
            st.session_state.account = acc
            st.session_state.runpage = 'profile'
            st.experimental_rerun()
    if st.button("Back"):
        st.session_state.runpage = 'profile'
        st.experimental_rerun()


def wishlist_page():
    acc = st.session_state.account
    st.header("Your Wishlist")
    items = (acc.wishlist)

    if items != 'NaN':
        items = (acc.wishlist).replace("\"", "").split(",")
        items = [int(item) for item in items if item.isnumeric()]
        item_objs = [item(ID=id) for id in items] 
        item_titles = [(i.title).replace("\"", "") for i in item_objs]
        item_descs = [(i.desc).replace("\"", "") for i in item_objs]
        item_links = [(i.link.replace("\"", "")) for i in item_objs]
        item_costs = [i.cost for i in item_objs]

        df = pd.DataFrame(list(zip(items, item_titles, item_descs, item_links, item_costs)), columns=('ID', 'Title', 'Description', 'Link', 'Cost'))
        df.set_index('ID', inplace=True)
        st.table(df)

    if st.button('Add item'):
        st.session_state.runpage = 'additem'
        st.experimental_rerun()
    if st.button('Modify item'):
        st.session_state.runpage = 'modifyitem'
        st.experimental_rerun()
    if st.button('Remove item'):
        st.session_state.runpage = 'deleteitem'
        st.experimental_rerun()
    if st.button('Back'):
        st.session_state.runpage = 'account'
        st.experimental_rerun()        

def additem_page():
    form = st.form(key='AddItemForm')
    title = form.text_input('Title:')
    desc = form.text_input('Description')
    link = form.text_input('Link')
    cost = form.text_input('Cost')
    
    case = -1
    chars = set("~!@#$%^&*()_+=")
    if form.form_submit_button('Add item'):
        if title == "":
            case = 0
        else:    
            if any((c in chars) for c in title):
                case = 1
        
        if cost != "":
            try: float(cost)    
            except ValueError: case = 2
        
        if case == 0: st.error("Title is not nullable")
        elif case == 1: st.error("Title can not contain symbols")
        elif case == 2: st.error("Cost must be a number")
        else: 
            i = item(title, desc, link, cost)
            acc = st.session_state.account
            a_name = acc.name
            a_surname = acc.surname
            a_birthday = acc.birthday
            a_email = acc.email
            a_notifications = acc.notifications
            a_username = acc.username
            a_password = acc.password
            a_interests = acc.interests
            a_wishlist = acc.wishlist
            a_friendlist = acc.friendlist
            if a_wishlist:
                a_wishlist += "," + str(i.itemID)
            else: 
                a_wishlist = str(i.itemID)
            
            acc.update_account(a_name, a_surname, a_birthday, a_email, a_notifications, a_username,a_password, a_interests, a_wishlist, a_friendlist)
            acc = Account(ID = int(acc.ID))
            st.session_state.account = acc
            st.session_state.runpage = 'wishlist'
            st.experimental_rerun()
    if st.button('Back'):
        st.session_state.runpage = 'wishlist'
        st.experimental_rerun() 


def modifyitem_page():
    acc = st.session_state.account
    items = (acc.wishlist).replace("\"", "").split(",")
    items = [int(item) for item in items]
    id =st.text_input('Please enter ID of the item you want to modify')
    if st.button('Confirm'):
        case = -1        
        try: 
            i = item(ID=int(id))
        except ValueError:
            case = 0
        
        try: int(id)
        except ValueError: 
            case = 1
        
        if case == 0: st.error("Item ID does not exist")
        elif case == 1: st.error("Item ID must be an integer")
        else:
            form = st.form(key='ModifyItemForm')
            title = form.text_input('Title:', value= i.title, placeholder= i.title)
            desc = form.text_input('Description', value= i.desc, placeholder= i.desc)
            link = form.text_input('Link', value= i.link, placeholder= i.link)
            cost = form.text_input('Cost', value= i.cost, placeholder= i.cost)
            chars = set("~!@#$%^&*()_+=")
            if form.form_submit_button('Modify item'):
                if title == "":
                    st.error("Title is not nullable")
                elif any((c in chars) for c in title):
                    st.error("Title can not contain symbols")
                elif cost != "":
                    try: 
                        float(cost)
                        print("modifying item")
                        i.modify_item(title, desc, link, cost)
                        st.session_state.runpage = 'wishlist'
                        st.experimental_rerun()    
                    except ValueError: st.error("Cost must be a number") 
                    
    if st.button('Back'):
        st.session_state.runpage = 'wishlist'
        st.experimental_rerun() 

def deleteitem_page():
    acc = st.session_state.account
    items = (acc.wishlist).replace("\"", "").split(",")
    items = [int(item) for item in items]
    form = st.form(key='DeleteItemForm')
    id =form.text_input('Please enter ID of the item you want to delete', value=items[0])
    case = -1
    
    if form.form_submit_button('Delete item'):
        try: 
            i = item(ID=int(id))
        except ValueError:
            case = 0
        
        try: int(id)
        except ValueError: 
            case = 1
        
        if case == 0: st.error("Item ID does not exist")
        elif case == 1: st.error("Item ID must be an integer")
        else:
            acc = st.session_state.account
            a_name = acc.name
            a_surname = acc.surname
            a_birthday = acc.birthday
            a_email = acc.email
            a_notifications = acc.notifications
            a_username = acc.username
            a_password = acc.password
            a_interests = acc.interests
            a_wishlist = acc.wishlist
            a_friendlist = acc.friendlist
    
            a_wishlist = a_wishlist.split(",")
            a_wishlist.remove(str(i.itemID))
            a_wishlist.remove('')
            a_wishlist = ','.join(a_wishlist)

            i.delete_item()
            acc.update_account(a_name, a_surname, a_birthday,a_email, a_notifications, a_username,a_password, a_interests, a_wishlist, a_friendlist)
            acc = Account(ID = int(acc.ID))
            
            st.session_state.account = acc
            st.session_state.runpage = 'wishlist'
            st.experimental_rerun()
    if st.button('Back'):
        st.session_state.runpage = 'wishlist'
        st.experimental_rerun() 

def friendlist_page():
    st.header('Friend List')
    acc = st.session_state.account
    friendlist = acc.friendlist
    if friendlist != 'NaN':        
        friendlist = friendlist.split(',')
        friendobj = [Account(ID=int(f)) for f in friendlist if f.isnumeric()]
        friendName = [f.name for f in friendobj]
        friendSur = [f.surname for f in friendobj]
        df = pd.DataFrame(list(zip(friendlist,friendName,friendSur)), columns=('ID', 'Name', 'Surname'))
        df.set_index('ID', inplace=True)
        st.table(df)
    if st.button('View Wishlist of friend'):
        st.session_state.runpage = 'friendwishlist'
        st.experimental_rerun() 
    if st.button('Add friend'):
        st.session_state.runpage = 'addfriend'
        st.experimental_rerun() 
    if st.button('Delete friend'):
        st.session_state.runpage = 'deletefriend'
        st.experimental_rerun() 
    if st.button('Back'):
        st.session_state.runpage = 'account'
        st.experimental_rerun()

def viewwishlist_page():
    acc = st.session_state.account
    friendlist = acc.friendlist
    friendlist = friendlist.split(',')
    form = st.form(key='Viewwishlistform')
    id =form.text_input('Please enter ID of the friend', value=friendlist[0])
    case = -1
    
    if form.form_submit_button('See wishlist'):
        try:
            friend = Account(ID=int(id))
            items = (friend.wishlist).replace("\"", "").split(",")
            items = [int(item) for item in items]
            item_objs = [item(ID=id) for id in items] 
        except ValueError: case = 0
        
        try: 
            Account(ID=int(id))
        except ValueError:
            case = 1
        
        try: int(id)
        except ValueError: 
            case = 2
        
        if case == 0: st.error("This ID doesn't have any wishlist")
        elif case == 1: st.error("Friend ID does not exist")
        elif case == 2: st.error("Friend ID must be an integer")
        else:
            item_titles = [(i.title).replace("\"", "") for i in item_objs]
            item_descs = [(i.desc).replace("\"", "") for i in item_objs]
            item_links = [(i.link.replace("\"", "")) for i in item_objs]
            item_costs = [i.cost for i in item_objs]
    
            df = pd.DataFrame(list(zip(items, item_titles, item_descs, item_links, item_costs)), columns=('ID', 'Title', 'Description', 'Link', 'Cost'))
            df.set_index('ID', inplace=True)
            st.dataframe(df)
    if st.button('Back'):
        st.session_state.runpage = 'friendlist'
        st.experimental_rerun() 

def addfriend_page():
    acc = st.session_state.account
    friendlist = acc.friendlist
    form = st.form(key='addfriend')
    id =form.text_input('Please enter ID of the friend')
    case = -1
    
    if form.form_submit_button('Add friend'):
        try: 
            friend = Account(ID=int(id))
        except ValueError:
            case = 0
        
        try: int(id)
        except ValueError: 
            case = 1
        
        if case == 0: st.error("Friend ID does not exist")
        elif case == 1: st.error("Friend ID must be an integer")
        else:
            if friendlist:
                friendlist += ',' + str(id)
            else:
                friendlist = str(id)
            a_name = acc.name
            a_surname = acc.surname
            a_birthday = acc.birthday
            a_email = acc.email
            a_notifications = acc.notifications
            a_username = acc.username
            a_password = acc.password
            a_interests = acc.interests
            a_wishlist = acc.wishlist
            
            acc.update_account(a_name, a_surname, a_birthday, a_email, a_notifications, a_username, a_password, a_interests, a_wishlist, friendlist)
            acc = Account(ID = int(acc.ID))
            st.session_state.account = acc
            st.session_state.runpage = 'friendlist'
            st.experimental_rerun() 
    if st.button('Back'):
        st.session_state.runpage = 'friendlist'
        st.experimental_rerun() 


def deletefriend_page():
    acc = st.session_state.account
    friends = (acc.friendlist).replace("\"", "").split(",")
    form = st.form(key='DeleteItemForm')
    id = form.text_input('Please enter ID of the friend want to delete', value=friends[0])
    case = -1
    
    if form.form_submit_button('Delete friend'):
        try: 
            Account(ID=int(id))
        except ValueError:
            case = 0
        
        try: int(id)
        except ValueError: 
            case = 1
        
        if case == 0: st.error("Friend ID does not exist")
        elif case == 1: st.error("Friend ID must be an integer")
        else:
            a_name = acc.name
            a_surname = acc.surname
            a_birthday = acc.birthday
            a_email = acc.email
            a_notifications = acc.notifications
            a_username = acc.username
            a_password = acc.password
            a_interests = acc.interests
            a_wishlist = acc.wishlist
    
            friends.remove(id)
            friends.remove('')
            friends = ','.join(friends)
    
            acc.update_account(a_name, a_surname, a_birthday, a_email, a_notifications, a_username, a_password, a_interests, a_wishlist, friends)
            acc = Account(ID = int(acc.ID))
            st.session_state.account = acc
            st.session_state.runpage = 'friendlist'
            st.experimental_rerun()
    if st.button('Back'):
        st.session_state.runpage = 'friendlist'
        st.experimental_rerun() 


if 'runpage' not in st.session_state:
    st.session_state.runpage = 'initial'

if 'account' not in st.session_state:
    st.session_state.account = 'None'

if st.session_state.runpage == 'initial':
    initial_page()
elif st.session_state.runpage == 'login':
    acc = login_page()
elif st.session_state.runpage == 'createaccount':
    acc = create_account()
elif st.session_state.runpage == 'account':
    account_page()
elif st.session_state.runpage == 'profile':
    profile_page()
elif st.session_state.runpage == 'editprofile':
    editprofile_page()
elif st.session_state.runpage == 'wishlist':
    wishlist_page()
elif st.session_state.runpage == 'additem':
    additem_page()
elif st.session_state.runpage == 'modifyitem':
    modifyitem_page()
elif st.session_state.runpage == 'deleteitem':
    deleteitem_page()
elif st.session_state.runpage == 'friendlist':
    friendlist_page()
elif st.session_state.runpage == 'friendwishlist':
    viewwishlist_page()
elif st.session_state.runpage == 'addfriend':
    addfriend_page()
elif st.session_state.runpage == 'deletefriend':
    deletefriend_page()