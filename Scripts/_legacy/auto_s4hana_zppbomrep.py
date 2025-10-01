# E600 :: FERTILIZANTES TOCANTINS
try:
    
    # Login to S/4HANA
    session = sap.login_to_s4hana()
    print("Logged in successfully!")

    # Definindo datas dinâmicas
    now = time.localtime()
    start_date = "01.01.2025"
    #end_day = now.day
    end_day = now.tm_mday
    if end_day>=10:
        end_day = str(end_day)
    else:
        end_day = '0' + str(end_day)

    #end_month = now.month
    end_month = now.tm_mon
    if end_month >= 10:
        end_month = str(end_month)
    else:
        end_month = '0' + str(end_month)

    #end_year = now.year
    end_year = now.tm_year

    session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "*60*"
    session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
    session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
    session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZPP_BOMREP_E600.XLSX"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
    session.findById("wnd[1]").sendVKey (0)

    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')

except Exception as e:
    print(f'Erro ao exportar dados do relatório ZPP_BOMREP para E600 :: {str(e)}')