import requests
import xml.etree.ElementTree as ET
from dateutil import parser
from datetime import date
import PySimpleGUI as sg
import datetime
import pandas as pd
import matplotlib.pyplot as plt



#PART 0. FUNCTIONS

# * * * * * * * * * * 

#FUNCTION to request data on the current USD rate

def news():

  layout_news_view = [[sg.Text('TODAY is ' + str(today.strftime("%d/%m/%Y")))]]

  window_NEWS_view = sg.Window('NEWS', layout_news_view, finalize = True)



  while True:

    event_NEWS_view, values_NEWS_view = window_NEWS_view.read()
    
    print(event_NEWS_view, values_NEWS_view)
    
    if event_NEWS_view == sg.WIN_CLOSED:

       break

    window_NEWS_view.close()

  return

# * * * * * * * * * * 

#FUNCTION to request data on the current USD rate

def USD_rate():

    #XML magic

    URL_USD = "https://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities.xml"

    response_USD = requests.get(URL_USD)

    with open('USD_MICEX.xml', 'wb') as USD_file:

        USD_file.write(response_USD.content)

    USD_file.close

    tree_USD = ET.parse('USD_MICEX.xml')

    root_USD = tree_USD.getroot()

    #Going to the right data on futures in the XML file

    data_marketdata = root_USD[1]

    rows_USD = data_marketdata[1]

    for row_USD in rows_USD:

        if row_USD.attrib['SECID'] == 'USDRUB_TMS':

            USD_to_return = row_USD.attrib['LAST']

    return USD_to_return


# * * * * * * * * * * 

#FUNCTION to request data and calculate the current forward rates

def FUTURES_view():

    #Preparing data containers for particular attributes

    today = date.today()

    USD_rate_now = USD_rate()

    FUTURES = pd.DataFrame()

    FUTURES_SECIDS = []

    FUTURES_SHORTNAMES = []

    FUTURES_LASTTRADEDATE = []

    FUTURES_DAYSTOEXPIRATION = []

    FUTURES_YIELD = []

    FUTURES_INITIALMARGIN = []

    FUTURES_LAST = []

    

    #XML magic

    URL_FUTURES = "https://iss.moex.com/iss/engines/futures/markets/FORTS/boards/RFUD/securities.xml"

    response_FUTURES = requests.get(URL_FUTURES)

    with open('futures_MICEX.xml', 'wb') as FUTURES_file:

        FUTURES_file.write(response_FUTURES.content)

    FUTURES_file.close

    tree_FUTURES = ET.parse('futures_MICEX.xml')

    root_FUTURES = tree_FUTURES.getroot()

    #Going to the right data on futures in the XML file

    data_securities = root_FUTURES[0]

    rows_FUTURES = data_securities[1]
    

    #Extracting data on partocular futures into separate lists

    for row_FUTURES in rows_FUTURES:

        if 'Si' in row_FUTURES.attrib['SHORTNAME']:

            FUTURES_SECIDS.append(row_FUTURES.attrib['SECID'])

            FUTURES_SHORTNAMES.append(row_FUTURES.attrib['SHORTNAME'])

            FUTURES_LASTTRADEDATE.append(row_FUTURES.attrib['LASTTRADEDATE'])

            #Determining the number of days till maturity

            date_futures_expiration = parser.parse(row_FUTURES.attrib['LASTTRADEDATE'])

            date_today = date.today().strftime('%Y-%m-%d %H:%M:%S')

            date_today = parser.parse(date_today)

            days_to_expiration = (date_futures_expiration - date_today).days

            FUTURES_DAYSTOEXPIRATION.append(str(days_to_expiration))

            

    FUTURES['SECID'] = FUTURES_SECIDS

    FUTURES['Futures'] = FUTURES_SHORTNAMES

    FUTURES['Last date'] = FUTURES_LASTTRADEDATE

    FUTURES['Days to expiration'] = FUTURES_DAYSTOEXPIRATION


    #Extracting data for current futures price from another dataset

    FUTURES_NAMES_TO_SEARCH = FUTURES['SECID'].tolist()

    print(FUTURES_NAMES_TO_SEARCH)

    data_marketdata = root_FUTURES[1]

    rows_marketdata_FUTURES = data_marketdata[1]

    for row_marketdata_FUTURES in rows_marketdata_FUTURES:

        if row_marketdata_FUTURES.attrib['SECID'] in FUTURES_NAMES_TO_SEARCH:

            FUTURES_LAST.append(row_marketdata_FUTURES.attrib['LAST'])

    FUTURES['Last price'] = FUTURES_LAST

    for last_price in FUTURES['Last price'].tolist():

        FUTURES_YIELD.append((float(last_price)-float(USD_rate_now)*1000)/(float(USD_rate_now)*1000)+1)

    FUTURES['Yield'] = FUTURES_YIELD

    FUTURES_YIELD = []

    for i_counter in range(0, len(FUTURES['Yield'].tolist())):

        FUTURES_YIELD.append("{:.2%}".format(FUTURES['Yield'].tolist()[i_counter]**(365/float(FUTURES['Days to expiration'].tolist()[i_counter]))-1))

    FUTURES['Yield'] = FUTURES_YIELD
                        
        


    #Forming the data for printing

    FUTURES = FUTURES.sort_values(by=['Last date'])

    FUTURES_to_list = FUTURES.values.tolist()



    layout_FORWARDS_view = [[sg.Text('TODAY is ' + str(today.strftime("%d/%m/%Y")))],
                            [sg.Table(values = FUTURES_to_list, headings=['SECID', 'Futures', 'Last date', 'Days to expiration','Last price', 'Yield'], max_col_width=85,
                    background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='right',
                    num_rows=10,
                    alternating_row_color='lightyellow',
                    key='-FUTURESTABLE-',
                    row_height=40,
                    enable_events = False,
                    tooltip='MICEX data')]]

    window_FORWARDS_view = sg.Window('FORWARD rates', layout_FORWARDS_view, finalize = True)



    while True:

        event_FORWARDS_view, values_FORWARDS_view = window_FORWARDS_view.read()
    
        print(event_FORWARDS_view, values_FORWARDS_view)
    
        if event_FORWARDS_view == sg.WIN_CLOSED:

            break

    window_FORWARDS_view.close()

    return


# * * * * * * * * * * 

#FUNCTION to request the current RUSFAR rate

def get_RUSFAR():

    URL_RUSFAR = "http://iss.moex.com/iss/engines/stock/markets/index/securities.xml"

    response_RUSFAR = requests.get(URL_RUSFAR)

    with open('indexes_MICEX.xml', 'wb') as RUSFAR_file:

        RUSFAR_file.write(response_RUSFAR.content)

    RUSFAR_file.close

    tree_RUSFAR = ET.parse('indexes_MICEX.xml')

    root_RUSFAR = tree_RUSFAR.getroot()

    search_results_RUSFAR = root_RUSFAR.findall(".//*[@SECID='" + "RUSFAR" + "']")

    data_securities_RUSFAR = search_results_RUSFAR[0].attrib

    data_marketdata_RUSFAR = search_results_RUSFAR[1].attrib

    #print(data_marketdata_RUSFAR['CURRENTVALUE'])

    return data_marketdata_RUSFAR['CURRENTVALUE'], data_marketdata_RUSFAR['SYSTIME']


# * * * * * * * * * * 

#FUNCTION to get MIACR data from CBR

def get_MIACR():

    today = date.today()

    #Getting fresh MIACR data from CBR

    URL = "http://www.cbr.ru/scripts/xml_mkr.asp?date_req1=10/01/2022&date_req2=" + today.strftime("%d/%m/%Y")

    response = requests.get(URL)

    with open('miacr.xml', 'wb') as file:

        file.write(response.content)

    file.close

    print(" ")
    
    #Doing XML mechanics

    tree = ET.parse('miacr.xml')

    root = tree.getroot()

    target_rate = tree.findall(".//Record[@Code='3']/C1")

    target_date = tree.findall(".//Record[@Code='3']")

    return target_date[-1].attrib["Date"], target_rate[-1].text


# * * * * * * * * * * 

#FUNCTION to obtain the current bond data from MICEX
#Inputs for if_above are: 0 - all data, 1 - Yield more than RUSFAR, 2- Yield more than 0%
#We will use data_bond countainer for a particular issue once it is selected according to the criteria. After that data_bond -> data_to_display

def get_bond_data(if_above, input_horizont, if_comission, if_VTBM_discount):

    data_to_display = []

    SECIDs = []

    input_horizont = int(input_horizont)

    #Getting fresh bond data from MICEX

    URL = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities.xml"

    response = requests.get(URL)

    with open('feed.xml', 'wb') as file:

        file.write(response.content)

    file.close


    #Doing XML mechanics

    tree = ET.parse('feed.xml')

    root = tree.getroot()

    print("Starting bonds screening.......")


    #Preparing the list of SECIDs falling within our time horizont

    for day_counter in range (0, input_horizont):

        search_date = date.today() + datetime.timedelta(days=day_counter)

        search_results_matdates = root.findall(".//*[@MATDATE='" + str(search_date) + "']")

        if search_results_matdates:

            for i_counter in range(0, len(search_results_matdates)):

                to_extract_SECID = search_results_matdates[i_counter].attrib

                SECIDs.append(to_extract_SECID['SECID'])


    #Preparing bonds' data for particular issues

    #print(SECIDs)

    for SECID in SECIDs:

        #Getting tags and attributes for particular security IDs

        search_results =[]

        search_results = root.findall(".//*[@SECID='" + SECID + "']")

        if len(search_results) == 3:

            data_securities = search_results[0].attrib

            data_marketdata = search_results[1].attrib

            data_marketdata_yields = search_results[2].attrib

        if len(search_results) == 2:

            data_securities = search_results[0].attrib

            data_marketdata = search_results[1].attrib


        #Filling data container for a particular bond
        
        data_bond = [] #empting container for a particular bond

        data_bond.append(str(SECID))

        data_bond.append(data_securities['SHORTNAME'])


        #Determining the number of days till maturity

        date_nextcoupon = parser.parse(data_securities['MATDATE'])

        date_today = date.today().strftime('%Y-%m-%d %H:%M:%S')

        date_today = parser.parse(date_today)

        days_to_maturity = (date_nextcoupon-date_today).days

        data_bond.append(str(days_to_maturity))


        #Getting basic pricing data to calculate Yield for Bid and Ask separately


        if data_marketdata['BID'] == "" or data_marketdata['OFFER'] == "":

            print ("No data for " + data_securities['SHORTNAME'])

        else:      


            #Calculation for BID

            price_Bid = float(data_securities['FACEVALUE'])*float(data_marketdata['BID'])/100

            accruedinterest = float(data_securities['ACCRUEDINT'])

            if if_comission:

                comission = comission_rate*(price_Bid+accruedinterest)

            else:

                comission = 0

            total_costs = price_Bid + accruedinterest + comission

            if int(data_securities['COUPONPERIOD']) < input_horizont and int(data_marketdata['DURATION']) > int(data_securities['COUPONPERIOD']):

                coupon = float(data_securities['COUPONVALUE'])*2

            else:

                coupon = float(data_securities['COUPONVALUE'])*1

            total_revenue = float(data_securities['FACEVALUE']) + coupon

            effective_days = (date_nextcoupon-date_today).days-1

            my_yield_Bid = (total_revenue / total_costs)**(365/effective_days)-1

            data_bond.append("{:.2%}".format(my_yield_Bid))

            data_bond.append(data_marketdata['BIDDEPTHT'])


            #Calculation for ASK
            
            price_Ask = float(data_securities['FACEVALUE'])*float(data_marketdata['OFFER'])/100

            accruedinterest = float(data_securities['ACCRUEDINT'])

            if if_comission:

                comission = comission_rate*(price_Ask+accruedinterest)

            else:

                comission = 0

            total_costs = price_Ask + accruedinterest + comission

            if int(data_securities['COUPONPERIOD']) < input_horizont and int(data_marketdata['DURATION']) > int(data_securities['COUPONPERIOD']):

                coupon = float(data_securities['COUPONVALUE'])*2

            else:

                coupon = float(data_securities['COUPONVALUE'])*1
            
            total_revenue = float(data_securities['FACEVALUE']) + coupon

            effective_days = (date_nextcoupon-date_today).days-1

            my_yield_Ask = (total_revenue / total_costs)**(365/effective_days)-1

            data_bond.append("{:.2%}".format(my_yield_Ask))

            data_bond.append(data_marketdata['OFFERDEPTHT'])

            data_bond.append("{:.2f}".format(float(data_marketdata['OFFERDEPTHT'])/float(data_marketdata['BIDDEPTHT'])))


            #Appending MICEX yield data

            if data_marketdata_yields:

                data_bond.append(data_marketdata_yields['EFFECTIVEYIELDWAPRICE'][0:5] + "%")

            else:

                data_bond.append("--")


            #Determining what is requested to display: All data(Else), Real deals(if_above==2), or Above RUSFAR (if_above==1)

            if if_above == 2:

                if my_yield_Ask > 0 and (my_yield_Bid / my_yield_Ask) < 1.3:

                    data_to_display.append(data_bond)

            elif if_above == 1:

                    if if_VTBM_discount: #VTBM discount is applied only to Above RUSFAR regime

                        if my_yield_Ask > (float(get_RUSFAR()[0])/100)*VTBM_discount:

                            data_to_display.append(data_bond)

                    if not if_VTBM_discount:

                        if my_yield_Ask > float(get_RUSFAR()[0])/100:

                            data_to_display.append(data_bond)
                
            else:

                data_to_display.append(data_bond)

    return data_to_display


# * * * * * * * * * * 

#FUNCTION to provide the current OFZ market analysis

def OFZ_view():

    today = date.today()

    print(' ')

    print("***")

    print(today)

    print(today.strftime("%d/%m/%Y"))


    #Getting fresh OFZ data from MICEX

    URL = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities.xml"

    response = requests.get(URL)

    with open('ofz.xml', 'wb') as file:

        file.write(response.content)

    file.close


    #Doing XML mechanics

    tree = ET.parse('ofz.xml')

    root = tree.getroot()

    data_securities = root[0]

   
    print('***')

    rows_data_securities = data_securities[1]

    print(rows_data_securities)

    print(rows_data_securities[0].attrib)
    

    #Getting data on particular OFZ

    SECIDS = []

    SECNAMES = []

    TYPES = []

    MATURITIES = []

    YIELDS_PREV = []

    DAYSTOMATURITY = []

    for row in rows_data_securities:

        to_load_secid = row.attrib["SECID"]

        to_load_secname = row.attrib["SECNAME"]

        to_load_type = ' '

        if 'ОФЗ-ПК' in to_load_secname:

            to_load_type = 'PK'

        if 'ОФЗ-ПД' in to_load_secname:

            to_load_type = 'PD'

        if 'ОФЗ-АД' in to_load_secname:

            to_load_type = 'AD'

        if 'ОФЗ-ИН' in to_load_secname:

            to_load_type = 'IN'


        to_load_maturity = row.attrib["MATDATE"]

        today = date.today().strftime('%Y-%m-%d %H:%M:%S')

        today = parser.parse(today)

        days_to_maturity = (parser.parse(to_load_maturity) - today).days

        to_load_yield = row.attrib["YIELDATPREVWAPRICE"]

        SECIDS.append(to_load_secid)

        SECNAMES.append(to_load_secname)

        TYPES.append(to_load_type)

        MATURITIES.append(to_load_maturity)

        YIELDS_PREV.append(to_load_yield)

        DAYSTOMATURITY.append(days_to_maturity)

    OFZ = pd.DataFrame()

    OFZ['SECIDs'] = SECIDS

    OFZ['SECNAMES'] = SECNAMES

    OFZ['TYPE'] = TYPES

    OFZ['MATURITIES'] = MATURITIES

    OFZ['Days to Maturity'] = DAYSTOMATURITY

    OFZ['Yield (prev WAPrice)'] = YIELDS_PREV

    OFZ = OFZ.sort_values(by=['Days to Maturity'])

    my_list = OFZ.values.tolist()


    OFZ_PD_to_plot = pd.DataFrame()

    OFZ_PD_to_plot = OFZ[(OFZ['TYPE'] == 'PD')]

    #print(OFZ_PD_to_plot)


    OFZ_PD_to_plot_2 = OFZ_PD_to_plot[(OFZ_PD_to_plot['Yield (prev WAPrice)'] != '0')]
    
    xData = OFZ_PD_to_plot_2['Days to Maturity'].tolist()

    xData = [float(x)/365 for x in xData]

    #print(xData)

    yData = OFZ_PD_to_plot_2['Yield (prev WAPrice)'].tolist()

    yData = [float(x) for x in yData]

    #print(yData)

    plt.scatter(xData, yData)

    plt.plot(xData, yData)

    plt.title("OFZ-PD Market at a glance on " + str(today.strftime("%d/%m/%Y")))

    plt.xlabel("Tenor (years)")

    plt.ylabel("Yield (%) as per MICEX")

    plt.grid(axis = 'both')

    plt.xticks([0,1,2,3,5,10, 15,20])

    plt.show()


    
    print("***")

    layout_view = [ [sg.Text('TODAY is ' + str(today.strftime("%d/%m/%Y")))],                    
                    
                    [sg.Table(values = my_list, headings=['SECIDs', 'SECNAMEs', 'TYPES', 'Muturity', 'Days to Maturity', 'Yield (prev WAPrice)'], max_col_width=85,
                    background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='right',
                    num_rows=15,
                    alternating_row_color='lightyellow',
                    key='-OFZTABLE-',
                    row_height=40,
                    enable_events = False,
                    tooltip='This is a table')]
                    ]

    window_view = sg.Window('OFZ MARKET VIEW', layout_view, finalize = True)



    while True:

        event_view, values_view = window_view.read()
    
        print(event, values)
    
        if event_view == sg.WIN_CLOSED:

            break

    window_view.close()
    
    return



# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#MAIN PROGRAM

#PART 1. VARIABLES

#Establishing variables

data_to_display = [] #To collect all data for all bonds

data_bond = [] #To collect data for a particular bond

time_horizont = 30 #Time period for investment in bonds

SECIDs = [] #To collec IDs of bond with maturities within our time horizont

comission_rate = 0.000467 #You broker's comission rate per one transaction (e.g. a buy or a sell transaction)

VTBM_discount = 0.93 #Discount of VTBM money market fund value increase per day as compared to RUSFAR ON 


#PART 2. CREATING GUI

sg.theme('Dark Green')

today = date.today()

data = data_to_display

headings = [' SECID ', ' SHORTNAME ', ' DaysTM ', ' Yield(Bid) ', 'Bid depth', ' Yield(Ask) ', 'Ask depth', 'Ask:Bid',' Yield MICEX ']

# ------ Window Layout ------
layout_main = [[sg.Text('TODAY is ' + str(today.strftime("%d/%m/%Y")))],
              #[sg.Text('_'*120)],
               [sg.Text('RUSFAR (on'), sg.Text(str(get_RUSFAR()[1])), sg.Text('):'), sg.Text(get_RUSFAR()[0]), sg.Text('%'), sg.VerticalSeparator(pad=None),
               sg.Text('MIACR for ON loans on ' + str(get_MIACR()[0]) + ': ' + get_MIACR()[1] + '%')],
               [sg.Button('OFZ market', key = '-MARKET-'), sg.Button('FUTURES rates', key = '-FUTURES-'), sg.Button('News', key = '-NEWS-')],

          [sg.Table(values=get_bond_data(0, time_horizont, True, False), headings=headings, max_col_width=55,
                    background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=True,
                    justification='right',
                    num_rows=10,
                    alternating_row_color='lightyellow',
                    key='-TABLE-',
                    row_height=30,
                    enable_events = True,
                    tooltip='This is a table')],
          [sg.Button('All deals', key = '-REFRESH-'),
           sg.Button('Yield(Ask) > RUSFAR', key = '-ABOVE-'),
           sg.Button('Real deals', key = '-REAL-')],
           [sg.Checkbox('Brokerage comission', enable_events=True, default = True, key = '-COMISSION-'), sg.Checkbox('VTBM discount on RUSFAR', enable_events=True, default = False, key = '-VTBM_DISCOUNT-'),

            sg.Text('Investment horizont (in days): '), sg.InputText(time_horizont, key = '-HORIZONT-', size = (5,1))]]
          
          
# ------ Create Window ------
window_main = sg.Window('Money market management toolkit v.0.5', layout_main, finalize = True)

#PART 3. RUSSING MAIN CYCLE WITH THE GUI

# ------ Event Loop ------
while True:
    event, values = window_main.read()
    
    print(event, values)

    if event == '-TABLE-':

      print(values['-TABLE-'])
    
    if event == sg.WIN_CLOSED:

        break

    if event == '-REFRESH-':

        if int(values['-HORIZONT-']) > 184 or int(values['-HORIZONT-']) < 1:

            sg.Popup('The horizont should be in range of 1..184 days')

        else:           

            window_main.Element('-TABLE-').Update(values = get_bond_data(0, values['-HORIZONT-'], values['-COMISSION-'], values['-VTBM_DISCOUNT-'])) 
       

    if event == '-ABOVE-':

        if int(values['-HORIZONT-']) > 184 or int(values['-HORIZONT-']) < 1:

            sg.Popup('The horizont should be in the range of 1..184 days')

        else:

            window_main.Element('-TABLE-').Update(values = get_bond_data(1, values['-HORIZONT-'], values['-COMISSION-'],  values['-VTBM_DISCOUNT-']))

    if event == '-REAL-':

        if int(values['-HORIZONT-']) > 184 or int(values['-HORIZONT-']) < 1:

            sg.Popup('The horizont should be in the range of 1..184 days')

        else:

            window_main.Element('-TABLE-').Update(values = get_bond_data(2, values['-HORIZONT-'], values['-COMISSION-'],  values['-VTBM_DISCOUNT-']))      

    if event == '-MARKET-':

        OFZ_view()


    if event == '-FUTURES-':

        FUTURES_view()

    if event == '-NEWS-':

        news()
    
window_main.close()