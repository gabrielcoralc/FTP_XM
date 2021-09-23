# -*- coding: utf-8 -*-
"""
Created on Wed May 12 10:40:05 2021

@author: Gabri
"""
import ftplib 
import io
import pandas as pd
import re 

def resumen_archivos(test_df,archivo):
    """La funcion toma un dataframe el cual contiene diferentes versiones de varios archivos.
    Retorna uns lista con la informacion resumida de las versiones que se encontro de cada archivo
    Parameters
    ----------
    test_df : dataframe
        dataframe con la informacion de los archivos dentro de una carpeta, previamente obtenidos
    archivo : str
        Nombre del archivo que se quiere obtener el resumen
    Returns
    -------
    versiones: list
        Lista que contiene las extensiones de cada archivo, en el caso de XM maneja varios archivos que se conocen como .TxF, .TxR, etc
    resumen: list
        Lista con la informacion resumida de los archivos pasados en test_df
    """
    resumen=[]
    if archivo == "all":
        archivos=test_df["archivo"].drop_duplicates().values
        for narchivo in archivos:
            versiones=test_df[test_df["archivo"]==narchivo]["version"].drop_duplicates().values
            #Generamos un resumen de los archivos aenc para facilitar su visualizacion
            for ver in versiones:
                version_resumida=test_df[(test_df["archivo"]==narchivo)&(test_df["version"]==ver)].iloc[0,1] + " - " + test_df[(test_df["archivo"]==narchivo)&(test_df["version"]==ver)].iloc[-1,1]
                resumen.append([narchivo,version_resumida,ver])
        return resumen, versiones
    else:
        versiones=test_df[test_df["archivo"]==archivo]["version"].drop_duplicates().values
        #Generamos un resumen de los archivos aenc para facilitar su visualizacion
        for ver in versiones:
            version_resumida=test_df[(test_df["archivo"]==archivo)&(test_df["version"]==ver)].iloc[0,1] + " - " + test_df[(test_df["archivo"]==archivo)&(test_df["version"]==ver)].iloc[-1,1]
            resumen.append([archivo,version_resumida,ver])
        return resumen, versiones

def ftpfile_to_df(ftp,filename):
    """La funcion lee un archivo subido en el servidor ftp y lo transforma en un objeto el cual puede ser reconocido por pandas
    y asi crear un dataframe
    ----------
    ftp : objeto
        objeto ftp con el cual se realizo la conexion al servidor
    filename : str
        Nombre del archivo que se pasara a dataframe
    Returns
    -------
    data: dataframe
        Dataframe con la informacion del archivo procesado
    """
    download_file = io.BytesIO()
    ftp.retrbinary("RETR {}".format(filename), download_file.write)
    download_file.seek(0) # after writing go back to the start of the virtual file
    data=pd.read_csv(download_file,sep=';',encoding='latin1')
    return data

def Consumos_aenc(ftp,test_df,opcion_year_mes):
    """Realiza el proceso de consolidar todos los archivos aencs cargados en la carpeta, ademas de dividir a cada uno de las
    fronteras por el factor que hace refiere la energia al STN.
    ----------
    ftp : objeto
        objeto ftp con el cual se realizo la conexion al servidor
    test_df : dataframe
        dataframe con la informacion de los archivos dentro de una carpeta, previamente obtenidos
    opcion_year_mes: str
        string que contiene el mes y año, esto sirve para identificar los archivos de manera mas sencilla
    Returns
    -------
    La funcion no retorna ningun valor, solo informa por pantalla que el proceso se ha completado con exito,
    y se genera un archivo excel con la informacion de los aenc, en la misma ruta en donde fue ejecutado el codigo
    """
    resumen_aenc, versiones=resumen_archivos(test_df,"aenc")
    print("\nSe presenta un resumen de los archivos AENC de la carpeta seleccionada:\n")
    print(pd.DataFrame(resumen_aenc,columns=["Archivo","Resumen-seriados","Version"]))
    print("\nSeleccione una de las versiones presentadas en la tabla para iniciar el proceso\n")
    version=""
    #Solicitamos la version del archivo con la que se va a trabar
    while version not in versiones:
        version=input()
        if version not in versiones:
            print("\nValor ingresado no es valido, favor revisar y ingresar una las opciones tal y como se muestra en el listado")
            
    ## Calculo de los factores con los archivos tfroc
    print("Iniciando recopilacion de los factores en archivo Tfroc")
    ################################################
    #1 Seccion calculo del factor de perdidas de cada frontera segun Tfroc
    tfrocs=test_df[(test_df["archivo"]=="tfroc") & (test_df["version"]==version)].values.tolist()
    filename=tfrocs[0][0]+tfrocs[0][1]+"."+tfrocs[0][2]
    variables=["CODIGO FRONTERA","FACTOR DE PERDIDAS","NIVEL DE TENSION","AGENTE COMERCIAL QUE IMPORTA","AGENTE COMERCIAL QUE EXPORTA"]
    Factor=ftpfile_to_df(ftp,filename)
    Factor=Factor[variables]
    tfrocs=tfrocs[1:]
    for tfroc in tfrocs:
        filename=tfroc[0]+tfroc[1]+"."+tfroc[2]
        print(filename)        
        conjuntoP=set(list(map(tuple,Factor.values.tolist())))
        data2=ftpfile_to_df(ftp,filename)
        data2=data2[variables]
        conjuntoS=set(list(map(tuple,data2.values.tolist())))
        #x for x in all_columns_list if x not in NotDesired]
        new_values=list(conjuntoS.difference(conjuntoP))
        
        for New_value in new_values:
            if New_value[0] in Factor["CODIGO FRONTERA"].values.tolist():
                Factor.loc[Factor["CODIGO FRONTERA"]==New_value[0],variables[1:]]=New_value[1:]
            else:
                Factor=Factor.append(pd.DataFrame({name:[val] for name,val in zip(variables,New_value)}),ignore_index=True)
    ########################################################################### 
    print("Factores Tfroc recopilados")
    ## Calculo de consumos AENC
    #############################################################################
    # 2 Seccion donde agrupamos los consumos de los aencs y procedemos a dividir entre el factor de perdida
    # de cada frontera para obtener sus valores reales de consumo
    print("Iniciando recopilacion de consumos aenc")
    aencs=test_df[(test_df["archivo"]=="aenc") & (test_df["version"]==version)].values.tolist()
    filename=aencs[0][0]+aencs[0][1]+"."+aencs[0][2]
    data=ftpfile_to_df(ftp,filename)
    data.insert(3,"FECHA",aencs[0][1][-2:]+"-"+aencs[0][1][:2]+"-"+opcion_year_mes.split("-")[0])
    aencs=aencs[1:]
    for aenc in aencs:
        filename=aenc[0]+aenc[1]+"."+aenc[2]
        provdata=ftpfile_to_df(ftp,filename)
        provdata.insert(3,"FECHA",aenc[1][-2:]+"-"+aenc[1][:2]+"-"+opcion_year_mes.split("-")[0])
        data=pd.concat([data,provdata])
    print("Finalizando y generando archivos excel con informacion")
    data['CODIGO SIC']=data['CODIGO SIC'].apply(lambda x: x.lower())
    data["CONSUMO_REFERIDO_STN"]=data.loc[:,"HORA 01":"HORA 24"].sum(axis=1)
    Factor["CODIGO FRONTERA"]=Factor["CODIGO FRONTERA"].apply(lambda x: x.lower())
    Frts=data[data["IMPO - EXPO"]!="OA"]["CODIGO SIC"].unique() #Asi obtenemos los frts de las fronteras que no son embebidas
    for Frt in Frts:
        data.loc[data["CODIGO SIC"]==Frt,"HORA 01":"HORA 24"]=data.loc[data["CODIGO SIC"]==Frt,"HORA 01":"HORA 24"]/(Factor[Factor["CODIGO FRONTERA"]==Frt][["FACTOR DE PERDIDAS"]].values.sum())
    data["CONSUMO_REFERIDO_OR"]=data.loc[:,"HORA 01":"HORA 24"].sum(axis=1)
    data["FECHA"]=pd.to_datetime(data["FECHA"],dayfirst=True) 
    Consumo_diarios=data.groupby(["CODIGO SIC","FECHA","IMPO - EXPO"]).sum().reset_index()[["CODIGO SIC","IMPO - EXPO","FECHA","CONSUMO_REFERIDO_OR"]].sort_values(["CODIGO SIC","IMPO - EXPO","FECHA"])
    Consumo_mensual=data.groupby(["CODIGO SIC","IMPO - EXPO"]).sum().reset_index()[["CODIGO SIC","IMPO - EXPO","CONSUMO_REFERIDO_OR","CONSUMO_REFERIDO_STN"]].sort_values(["CODIGO SIC","IMPO - EXPO"])
    Consumo_mensual.to_excel("Consumo_Mes_aenc_"+opcion_year_mes.split("-")[0]+"_"+opcion_year_mes.split("-")[1]+"_"+version+".xlsx")
    Consumo_diarios.to_excel("Consumo_Mes_dia_aenc_"+opcion_year_mes.split("-")[0]+"_"+opcion_year_mes.split("-")[1]+"_"+version+".xlsx")
    print("\nProceso exitoso")

def consolidado_archivo(Archivos_df,ftp,opcion_year_mes):
    """Realiza el proceso de consolidar todos los archivos, de cierto formato, sin procesos adicionales
    ----------
    ftp : objeto
        objeto ftp con el cual se realizo la conexion al servidor
    Archivos_df : dataframe
        dataframe con la informacion de los archivos dentro de una carpeta, previamente obtenidos
    opcion_year_mes: str
        string que contiene el mes y año, esto sirve para identificar los archivos de manera mas sencilla
    Returns
    -------
    La funcion no retorna ningun valor, solo informa por pantalla que el proceso se ha completado con exito,
    y se genera un archivo excel con la informacion consolidada, en la misma ruta en donde fue ejecutado el codigo
    """
    archivos=Archivos_df["archivo"].drop_duplicates().values
    string_lista1=""
    for x in archivos:
        string_lista1+="- " + x + "\n"
    print(f"""\nA continuacion se muestran los archivos disponibles para realizar su consolidado:
{string_lista1}\n
Ingrese el nombre del archivo a procesar: """)
    opcion_archivo=""
    while opcion_archivo not in archivos:
        opcion_archivo=input()
        if opcion_archivo not in archivos:
            print("\nValor ingresado no es valido, favor revisar y ingresar una las opciones tal y como se muestra en el listado")
    resumen, versiones=resumen_archivos(Archivos_df,opcion_archivo)
    print(f"\nSe presenta un resumen de los archivos {opcion_archivo} de la carpeta seleccionada:\n")
    print(pd.DataFrame(resumen,columns=["Archivo","Resumen-seriados","Version"]))
    print("\nSeleccione una de las versiones presentadas en la tabla para iniciar el proceso\n")
    version=""
    #Solicitamos la version del archivo con la que se va a trabar
    while version not in versiones:
        version=input()
        if version not in versiones:
            print("\nValor ingresado no es valido, favor revisar y ingresar una las opciones tal y como se indico en el listado")
    ## Procedemos a cargar los archivos y unirlos en uno solo
    print("Iniciando consolidacion del archivo")
    archivos=Archivos_df[(Archivos_df["archivo"]==opcion_archivo) & (Archivos_df["version"]==version)].values.tolist()
    filename=archivos[0][0]+archivos[0][1]+"."+archivos[0][2]
    Consolidado_df=ftpfile_to_df(ftp,filename)
    archivos=archivos[1:]
    for archivo in archivos:
        filename=archivo[0]+archivo[1]+"."+archivo[2]
        print(filename)
        data=ftpfile_to_df(ftp,filename)
        Consolidado_df=pd.concat([Consolidado_df,data])
    Consolidado_df.to_excel(opcion_archivo+"_"+opcion_year_mes.split("-")[0]+"_"+opcion_year_mes.split("-")[1]+"_"+version+".xlsx")
    print("\nProceso finalizado, se ha creado un archivo en excel para el consolidado de informacion de "+ opcion_archivo)
######################################################################   
## PARTE PRINCIPAL DEL CODIGO    
if __name__=="__main__":
    
    FTP_HOST = "sv01.xm.com.co"  #Servidor FTP
    FTP_USER = "Usuario_XM" #Usuario
    FTP_PASS = "password"  #Password
    Siglas_comercializador="NNNN"
    op_estado="1"        ##El estado que maneja los menus
    while op_estado != "0":
        # connect to the FTP server
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        ftp.cwd("/UsuariosK/"+Siglas_comercializador+"/SIC/COMERCIA/") #Conexion a la carpeta referentes a los consumos de las fronteras en los AENCs, en este caso se lo ubica en la carpeta de la fronteras relacionadas con CEDENAR
        carpetas=ftp.nlst()  #Lista de las carpetas en la ubicacion del puntero ftp
        string_lista1=""
        i=0
        for x in carpetas:
            if i<6:
                string_lista1+="- " + x + "\t"
                i+=1
            else:
                string_lista1+="\n" + "- " + x + "\t"
                i=1
        print(f"""Bienvenido al sistema de adquisicion de consumos AENC publicados por XM
\nA continuacion se presenta el listado de carpetas disponibles para acceder:
    
{string_lista1}\n""")
        print("Para iniciar el proceso, favor ingrese el nombre de la carpeta a acceder:")
        opcion_year_mes=""
        while opcion_year_mes not in carpetas:
            opcion_year_mes=input()
            if opcion_year_mes not in carpetas:
                print("\nValor ingresado no es valido, favor revisar y ingresar una las opciones tal y como se muestra en el listado")
        
        ftp.cwd(opcion_year_mes) #Ingresamos a la carpeta seleccionada
        archivos=ftp.nlst()   #Lista de archivos dentro de la carpeta
        #Tomamos la informacion de los archivos dentro de la carpeta
        #Y separamos la cadena para entender el nombre del archivo y su version
        test=[x.split(".") for x in archivos] #separamos las extensiones de los archivos
        test2=[re.split('(\d.*)',x[0])[0:2] for x in test] # Separamos la parte que tiene letras de la que tiene numeros
        Archivos_df=pd.DataFrame([y+[x[1]] for x,y in zip(test,test2)],columns=["archivo","seriado","version"])#Juntamos todo en un Df
        Opciones_estado=["0","1","2","3","anterior"]
        op_estado="1"
        while op_estado != "0" and op_estado != "anterior":
            print("""\nIngrese el numero del proceso que desea realizar en la carpeta seleccionada:
                
1 - Descargar los consumos consolidados de las fronteras segun lo reportado en el AENC
2 - Visualizar un resumen general de todos los archivos dentro de la carpeta
3 - Descargar el consolidado de un archivo en concreto
                
En caso de querer salir de la aplicacion ingrese el numero 0
En caso de querer seleccionar otra carpeta escriba anterior""")
            op_estado=""
            while op_estado not in Opciones_estado:
                op_estado=input()
                if op_estado not in Opciones_estado:
                    print("\nValor ingresado no es valido, favor revisar y ingresar una las opciones tal y como se muestra en el listado")
            if op_estado=="1":
                Consumos_aenc(ftp,Archivos_df,opcion_year_mes)
            elif op_estado=="2":
                resumen,versiones=resumen_archivos(Archivos_df,"all")
                print("\nSe presenta un resumen general de los archivos que se encuentran en la carpeta:\n")
                print(pd.DataFrame(resumen,columns=["Archivo","Resumen-seriados","Version"]))
            elif op_estado=="3":
                consolidado_archivo(Archivos_df,ftp,opcion_year_mes)
    print("\nGracias por utilizar la aplicacion, que tenga buen dia")
        