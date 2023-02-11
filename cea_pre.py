# -*- coding: utf-8 -*-
"""
Generate NASA-CEA input files "*.inp"

Brief Description:
This program generates "*.inp" files assigning each condition
as a command line. Generated .inp files will be located in the
assigned case name folder under "cea_db/inp" directory. Also
you can utilize indivisual functions such as "make_inp()", 
"make_inp_name()" for generating one specific .inp file.

This module provide some functions or classes as the followings;
* make_inp: function for generating one specific .inp file, when
            you assign chem species as "oxid" and "fuel" in *.inp.
* make_inp_name: function for generating one specific .inp file, when
            you assign chem species as "name" in *.inp.
* Cui_input: class for assigning conditions and generating .inp files

Author: T.J.
Created: 04/01/2018
Revised: 05/08/2021
Version: 3.1.0 (BETA)
"""

import os
import copy
import numpy as np
import pandas as pd
import json
from tqdm import tqdm

class Cui_input():
    """
    Class to attract information through CUI to generate .inp file
    
    Parameters
    ----------
    langlist: list ["jp","en",...]
        Contain initial two characters of language name.
    
    sntns_df : dict {outer_key: innerdict, ...}
        outer_key: string\n
            it is representative of the questionaire type. \n
        innerdict: string\n
            it is a questionaier sentense.

    lang: string
        Selected language from the "langlist"
    
    option: int
        represented number
        0: equilibrium during expansion
        1: frozen after the end of chamber
        2: frozen after nozzle throat
    
    oxid: string
        must use a symbol written in NASA RP-1311-P2 app.B
        
    fuel: string
        fuel name. It isn't necessary to select from NASA RP-1311-P2 app.B
    
    o_itemp: float
        Oxidizer initial temperature [K]

    f_itemp: float
        Fuel initial temperature [K]

    f_enthlpy: float
        Fuel satndard enthalpy of formation [kJ/mol]
    
    f_elem: dict, {"A": num, ...}
        A: string, symbol of contained element in fuel
        num: int, the number of element contained in 1 mol fuel [mol]
        
    eps: float
        Nozzle area ratio, Ae/At.
    """
    
    langlist = ["jp","en"]
    _tmp_ = dict()
    _tmp_["option"] = {"jp": "\n計算オプション(0~2)を選択してください．\n例: 0: 全域平衡計算\n    1: 燃焼器内のみ平衡計算\n    2: スロートまで平衡計算",
                     "en": "\nPlease select option (0-2) of calculation.\ne.g.: 0: equilibrium during expansion\n      1: frozen after the end of chamber\n      2: frozen after nozzle throat"}

    _tmp_["oxid"] = {"jp": "\n酸化剤の種類を入力してください.\n*記号はNASA RP-1311-P2 app.B に準拠\n例: O2(L)",
                     "en": "\nPlease input oxidizer name.\n*Concerning spiecies name, please refer \"NASA RP-1311-P2 app.B.\"\ne.g.: O2(L)"}

    _tmp_["fuel"] = {"jp": "\n燃料の名前を入力してください\n例: PMMA",
                     "en": "\nPlease input fuel name.\"\ne.g.: PMMA"}

    _tmp_["other"] = {"jp": "\nその他の物質の名前を入力してください\n例: N2",
                      "en": "\nPlease input the names of other chemical species.\"\ne.g.: N2"}

    _tmp_["omit"] = {"jp": "\n計算から除外したい物質の名前を半角スペースで区切って入力してください\n例: C(gr) H2O(cr)",
                      "en": "\nPlease input the names of chemical species for omitting from calculation with separating by a space.\"\ne.g.: C(gr) H2O(cr)"} 

    _tmp_["only"] = {"jp": "\n計算で考慮する化学種を限定したい物質の名前を半角スペースで区切って入力してください\n例: CO2 H2O CO OH",
                      "en": "\nPlease input the names of chemical species for manually assigning in the calculation with separating by a space.\"\ne.g.:  CO2 H2O CO OH"}    

    _tmp_["o_wt"] = {"jp": "\n酸化剤の質量分率[%]を入力してください",
                     "en": "\nPlease input oxidizer mass fraction [%]"}
    
    _tmp_["f_wt"] = {"jp": "\n燃料の質量分率[%]を入力してください",
                     "en": "\nPlease input fuel mass fraction [%]"}

    _tmp_["ot_wt"] = {"jp": "\nその他の化学物質の質量分率[%]を入力してください\n注：推進剤全体に対する質量分率です　この値は固定されます",
                      "en": "\nPlease input the mass fraction of other chemical species [%]\nnote: the mass fraction is for all propellant mass This value is fixed at every O/F condition"}

    _tmp_["o_itemp"] = {"jp": "\n酸化剤の初期温度[K]を入力してください",
                     "en": "\nPlease input initial oxidizer temperature [K]"}
    
    _tmp_["f_itemp"] = {"jp": "\n燃料の初期温度[K]を入力してください",
                     "en": "\nPlease input initial fuel temperature [K]"}

    _tmp_["ot_itemp"] = {"jp": "\nその他の化学種の初期温度[K]を入力してください",
                         "en": "\nPlease input the initial fuel temperature of other chemical species [K]"}

    _tmp_["o_enthlpy"] = {"jp": "\n酸化剤の標準生成エンタルピ[kJ/mol]を入力してください",
                     "en": "\nPlease input standard enthalpy of formation [kJ/mol] respect to oxidizer"}
    
    _tmp_["f_enthlpy"] = {"jp": "\n燃料の標準生成エンタルピ[kJ/mol]を入力してください",
                     "en": "\nPlease input standard enthalpy of formation [kJ/mol] respect to fuel"}

    _tmp_["ot_enthlpy"] = {"jp": "\nその他の化学種の標準生成エンタルピ[kJ/mol]を入力してください",
                           "en": "\nPlease input standard enthalpy of formation [kJ/mol] respect to other chemical species"}

    _tmp_["o_elem"] = {"jp": "\n1molの酸化剤に含まれる元素とそのmol数を入力してください.\n例: N 2 O 1",
                     "en": "\nPlease input the element symbols and its mol number contained per 1 mol of oxidizer\ne.g.: N 2 O 1"}
    
    _tmp_["f_elem"] = {"jp": "\n1molの燃料に含まれる元素とそのmol数を入力してください.\n例: C 5 H 2 O 6",
                     "en": "\nPlease input the element symbols and its mol number contained per 1 mol of fuel\ne.g.: C 5 H 2 O 6"}

    _tmp_["ot_elem"] = {"jp": "\n1molの化学種に含まれる元素とそのmol数を入力してください.\n例: C 5 H 2 O 6",
                        "en": "\nPlease input the element symbols and its mol number contained per 1 mol of chemical species\ne.g.: N 2"}

    _tmp_["eps"] = {"jp": "\n開口比Ae/Atを入力してください.",
                    "en": "\nPlease input the area ratio, Ae/At."}
    
    _tmp_["of"] = {"jp": "\n計算するO/Fの範囲を入力してください.\n許容範囲：0.01~99.99 , 最小刻み幅：0.01\n例) 0.5~10 を 0.1毎に計算する場合.\n0.5　10.1　0.1",
                "en": "\nPlease input the range of O/F where you want to calculate.\nRange: 0.01 ~ 99.99, Minimum interval: 00.1\ne.g. If the range is 0.5 to 10 and the interval is 0.1\n0.5 10.1 0.1"}

    _tmp_["Pc"] = {"jp": "\n\n計算する燃焼室圧力[MPa]の範囲を入力してください.\n許容範囲：0.2~100 MPa, 最小刻み幅：0.01　MPa\n例) 0.5~5.0 MPa を 0.1 MPa毎に計算する場合.\n0.5　5.1　0.1",
                "en": "\nPlease input the range of Chamber pressure [MPa] where you want to calculate.\nRange: 0.2~100 MPa, Minimum interval: 0.01 MPa\ne.g. If the range is 0.5 to 5.1 MPa and the interval is 0.1 MPa\n0.5 5.0 0.1"}

    _tmp_["cont_react"] = {"jp": "\n化学種の入力を続けますか? \"y/n\"",
                "en": "\nDo you want to continue inputting reactant information? \"y/n\""}

    _tmp_["cont_enthlpy"] = {"jp": "\n標準生成エンタルピと構成元素を手動入力しますか? \"y/n\"",
                "en": "\nDo you want to manually input standard enthalpy and constitution of element? \"y/n\""}

    _tmp_["cont_other"] = {"jp": "\n酸化剤または燃料以外の物質を入力しますか? \n注：ここで入力された物質は後に指定するO/Fによらず以下で指定する割合で含まれるようになります \"y/n\"",
                      "en": "\nDo you want to assign other chemical species which are not oxidizer or fuel?\
                             \nnote: Assigned species at the following query will be contained in the propellant with a certain mass fraction, which is not affected by assigned O/F \"y/n\""}

    _tmp_["cont_omit"] = {"jp": "\n計算から除外したい物質を入力しますか? \"y/n\"",
                      "en": "\nDo you want to assign chemical species for omitting from calculation? \"y/n\""}

    _tmp_["cont_only"] = {"jp": "\n計算で考慮する物質を手動で入力しますか? \"y/n\"",
                      "en": "\nDo you want to manually assign chemical species considered in calculation? \"y/n\""}

    _tmp_["confirm"] = {"jp": "\n入力した内容は正確ですか? \"y/n\"",
                "en": "\nIs the inputted data correct? \"y/n\""}

    _tmp_["jsconf"] = {"jp": "\n既に存在する cond.json ファイルから計算条件を読み込みますか？ \"y/n\"",
                "en": "\nDo you want to read the calculating conditioin from existing \"cond.json\"? \"y/n\""}

    _tmp_["casename"] = {"jp": "\n計算ケース名（フォルダ名）を入力して下さい．",
                "en": "\nInput a Case Name (Folder Name)"}
   

    def __init__(self):
        self.sntns_df = pd.DataFrame([], columns=self.langlist)
        for i in self._tmp_:    # read and contain question sentense list to pandas data-frame
            self.sntns_df = self.sntns_df.append(pd.DataFrame(self._tmp_[i], index=[i]))
        self._inp_lang_()   # Language selection
        self.fld_path = self._getpath_()    # get folder path
        if os.path.exists(os.path.join(self.fld_path, "cond.json")):
            ## when read a calculating condition from cond.json, flag == True, if not, flag == False
            flag = self._conf_readjs_()
        else:
            ## when program could not find cond.json, flag == False
            flag = False
        if flag:
            self._read_json_(self.fld_path)
        else:
            self._inp_option_()
            self.list_oxid = self._inp_react_("oxid")   # get oxidizer condition
            self.list_fuel = self._inp_react_("fuel")   # get fuel condition 
            if self._inp_option_other_():               # get other chemical species list, which are not oxidizer and fuel.
                self.list_other = self._inp_react_("other")
            else:
                self.list_other = []
            if self._inp_option_omit_only_("omit"):     # get "omit" list
                self.omit = self._inp_omit_only_list_("omit")
            else:
                self.omit=[]
            if self._inp_option_omit_only_("only"):     # get "only" list
                self.only = self._inp_omit_only_list_("only")
            else:
                self.only=[]
            self._inp_eps_()    # get nozzle area expantion ratio
            self._inp_of_()     # get calcuating O/F range
            self._inp_Pc_()     # get calcuating Pc range

    def _inp_lang_(self):
        """
        Select user language
        """
        print("Please select language.\n{}".format(self.langlist))
        lang = input(">> ")
        if lang in self.langlist:
            self.lang = lang
        else:
            print("There is no such language set!")

    def _getpath_(self):
        """
        Return the folder path which will cantain cea files: .inp, .out and csv cea-database
        """
        cadir = os.path.dirname(os.path.abspath(__file__))
        print(self.sntns_df[self.lang]["casename"])
        foldername = str(input(">> "))
        path = os.path.join(cadir, "cea_db", foldername)
        return(path)

    def _conf_readjs_(self):
        """
        Confirm whether reading a json condition file or not.

        Return
        -------
        flag: bool
        """
        while True:
            print(self.sntns_df[self.lang]["jsconf"])
            option = str(input(">> "))
            if option == "y":
                flag = True
                break
            elif option == "n":
                flag = False
                break
            else:
                print("Please re-confirm the input answer. Input \"y\" or \"n\"")
        return flag

    def _inp_option_(self):
        """
        Select a option of calculation: whether equilibrium or frozen composition.
        """
        print(self.sntns_df[self.lang]["option"])
        option = int(input(">> "))
        if option == 0:
            option = "equilibrium"
        elif option == 1:
            option = "frozen nfz=1" # frozen composition after the end of chamber
        elif option == 2:
            option = "frozen nfz=2" # frozen composition after nozzle throat
        else:
            print("Please re-confirm input integer!")
        self.option = option

    def _inp_option_other_(self):
        """
        Select an option whether assign other chemical species, which are not oxid or fuel, or not.
        """
        while True:
            print(self.sntns_df[self.lang]["cont_other"])
            option = str(input(">> "))
            if option == "y":
                res = True
                break
            elif option == "n":
                res = False
                break
            else:
                print("Please re-confirm the input answer. Input \"y\" or \"n\"")
        return res

    def _inp_react_(self, ident):
        """
        Input chemical species as just a type of "name".
        """
        while(True):
            list_react = []
            while(True):
                name = self._inp_name_(ident)
                wt = self._inp_wt_(ident)
                temp = self._inp_temp_(ident)
                print(self.sntns_df[self.lang]["cont_enthlpy"])
                flag = input(">> ")
                if flag == "y":
                    enthalpy = self._inp_enthlpy_(ident)
                    elem = self._inp_elem_(ident)
                else:
                    enthalpy = ""
                    elem = ""
                list_react.append({"name": name,
                                  "wt": wt,
                                  "temp": temp,
                                  "h": enthalpy,
                                  "elem": elem})
                print(self.sntns_df[self.lang]["cont_react"])
                flag = input(">> ")
                if flag == "n":
                    break
            print(self.sntns_df[self.lang]["confirm"])
            print(list_react)
            flag = input(">> ")
            if flag == "y":
                break
        return(list_react)

    def _inp_name_(self, ident):
        """
        Input chemical species as "fuel", "oxid", or "name".
        """
        if ident == "fuel":
            print(self.sntns_df[self.lang]["fuel"])
        elif ident == "oxid":
            print(self.sntns_df[self.lang]["oxid"])
        elif ident == "other":
            print(self.sntns_df[self.lang]["other"])
        name = input(">> ")
        return(name)

    def _inp_wt_(self, ident):
        """
        Input weight fraction of oxidizer, fuel or other species
        """
        if ident == "fuel":
            print(self.sntns_df[self.lang]["f_wt"])
        elif ident == "oxid":
            print(self.sntns_df[self.lang]["o_wt"])
        elif ident == "other":
            print(self.sntns_df[self.lang]["ot_wt"])
        wt = float(input(">> "))
        return(wt)

    def _inp_temp_(self, ident):
        """
        Input initial temperature of propellant
        """
        if ident == "fuel":
            print(self.sntns_df[self.lang]["f_itemp"])
        elif ident == "oxid":
            print(self.sntns_df[self.lang]["o_itemp"])
        elif ident == "other":
            print(self.sntns_df[self.lang]["ot_itemp"])            
        temp = float(input(">> "))
        return(temp)
    
    def _inp_enthlpy_(self, ident):
        """
        Input fuel standard enthalpy of formation
        """
        if ident == "fuel":
            print(self.sntns_df[self.lang]["f_enthlpy"])
        elif ident == "oxid":
            print(self.sntns_df[self.lang]["o_enthlpy"])
        elif ident == "other":
            print(self.sntns_df[self.lang]["ot_enthlpy"])
        enthalpy = float(input(">> "))
        return(enthalpy)
        
    def _inp_elem_(self, ident):
        """
        Input element contained in fuel and its mol number contained in per 1 mol
        """
        if ident == "fuel":
            print(self.sntns_df[self.lang]["f_elem"])
        elif ident == "oxid":
            print(self.sntns_df[self.lang]["o_elem"])
        elif ident == "other":
            print(self.sntns_df[self.lang]["ot_elem"])
        elem = input(">> ")
        return(elem)

    def _inp_omit_only_list_(self, mode):
        """
        Input chemical species for omitting from and limitting in the calculation.
        This method for "omit" and "only" optioin in NASA-CEA.
        """
        if mode == "omit": 
            print(self.sntns_df[self.lang]["omit"])
        elif mode == "only":
            print(self.sntns_df[self.lang]["only"])
            pass
        species = list(map(lambda x: str(x) ,input(">> ").split()))
        return species

    def _inp_option_omit_only_(self, mode):
        """
        Select an option whether assign omit and only chemical species or not.
        """
        while True:
            if mode == "omit":
                print(self.sntns_df[self.lang]["cont_omit"])
            elif mode == "only":
                print(self.sntns_df[self.lang]["cont_only"])
            option = str(input(">> "))
            if option == "y":
                res = True
                break
            elif option == "n":
                res = False
                break
            else:
                print("Please re-confirm the input answer. Input \"y\" or \"n\"")
        return res
                
    def _inp_eps_(self):
        """
        Input nozzle-area ratio
        """      
        print(self.sntns_df[self.lang]["eps"])
        self.eps = float(input(">> "))
        
    def _inp_of_(self):
        """
        Input calculation range of O/F
        """      
        print(self.sntns_df[self.lang]["of"])
        self.of = list(map(lambda x: float(x) ,input(">> ").split()))
      
    def _inp_Pc_(self):
        """
        Input calculation range of chamber pressure, Pc.
        """      
        print(self.sntns_df[self.lang]["Pc"])
        self.Pc = list(map(lambda x: float(x) ,input(">> ").split()))

    def _read_json_(self, fldpath):
        """
        Read a input calculation condition from a json file "cond.json"
        
        Parameters
        ----------
        fldpath : string
            folder path
        """
        with open(os.path.join(fldpath, "cond.json"), "r") as jsread:
            dic = json.load(jsread)
        self.option = dic["option"]
        self.list_oxid = dic["oxid"]
        self.list_fuel = dic["fuel"]
        self.list_other = dic["other"]
        self.omit = dic["omit"]
        self.only = dic["only"]
        self.eps = dic["eps"]
        self.Pc = dic["pc_range"]
        self.of = dic["of_range"]

    def _make_json_(self, fldpath):
        """
        Generate a input calculation condition as a json file
        
        Parameters
        ----------
        fldpath : string
            folder path
        """
        option = self.option
        oxid = self.list_oxid
        fuel = self.list_fuel
        other = self.list_other
        omit = self.omit
        only = self.only
        eps = self.eps
        pc = self.Pc
        of = self.of
        dic = {"option": option,
               "oxid": oxid,
               "fuel": fuel,
               "other": other,
               "omit": omit,
               "only": only,
               "eps": eps,
               "pc_range": pc,
               "of_range": of
               }
        with open(os.path.join(fldpath, "cond.json") ,"w") as jsout:
            json.dump(dic, jsout, indent=4)
        


    def gen_all(self):
        """
        Generate input file with respect to every condition
        
        Parameters
        ----------
        path: string
            Folder path where this function will make "inp" floder storing ".inp"
    
        func: function    
        -----------------
        (oxid, fuel, dh, Pc, of, n, elem) = func(path)
         
        Parameters
            path: string\n
        Returns
            oxid: string, e.g."oxid=O2(L) wt=100 t,k=90.15"  \n
            fuel: string, e.g."fuel=PMMA wt=100 t,k=298.15"  \n
            dh: float  \n
            Pc: list, [start, end, interval], each element type is float  \n
            of: list, [start, end, interval], each element type is float  \n
            
        """
        path = os.path.join(self.fld_path, "inp")
        of = np.arange(self.of[0], self.of[1], self.of[2])
        Pc = np.arange(self.Pc[0], self.Pc[1], self.Pc[2])
        if len(self.list_other) != 0:
            wt_other = sum([dic["wt"] for dic in self.list_other])
            num_round = int(2) #the number of decimal places in "Pc" & "of"
            list_oxid = copy.deepcopy(self.list_oxid)
            list_fuel = copy.deepcopy(self.list_fuel)

        for i in tqdm(range(np.size(Pc))):
            for j in range(np.size(of)):
                if len(self.list_other) == 0:
                    make_inp(path, self.option, of[j], Pc[i], self.list_oxid, self.list_fuel, self.eps, list_omit=self.omit, list_only=self.only)
                else:
                    Yo = (1.0-wt_other*1e-2)/(1 + 1/of[j])  # oxid mass fraction for all propellant mass
                    Yf = (1.0-wt_other*1e-2)/(1 + of[j])    # fuel mass fraction for all propellant mass
                    for k, dic in enumerate(self.list_oxid):
                        list_oxid[k]["wt"] = round(dic["wt"]*Yo, 5)
                    for k, dic in enumerate(self.list_fuel):
                        list_fuel[k]["wt"] = round(dic["wt"]*Yf, 5)
                    list_species = list_oxid + list_fuel + self.list_other
                    fname = "Pc_{:0>5.2f}__of_{:0>5.2f}".format(round(Pc[i],num_round), round(of[j],num_round)) #.inp file name, e.g. "Pc=1.00_of=6.00"
                    make_inp_name(path, self.option, list_species, Pc[i], self.eps, list_omit=self.omit, list_only=self.only, fname=fname)
        self._make_json_(self.fld_path) # make condition file as json
        return(self.fld_path)



def make_inp(path, option, of, Pc, list_oxid, list_fuel, eps, list_omit=[], list_only=[], fname=False):
    """
    Write information in input file, "*.inp".
    
    Parameter
    ---------
    path : string
        Path at which "*.inp" file is saved
    option: string
        Calculation option, wtheher using equilibrium composition or frozen composition.
    of: float,
        O/F
    Pc: float,
        Camberpressure, [MPa]
    list_oxid: list of dictionary
        The list has an information about oxidizer as dict type; dict{"name":name, "wt":weight fraction %, "temp": initial temperature K, "h": enthalpy kJ/mol, "elem": element}
    list_fuel: list of dictionary
        The list has an information about fuel as dict type; dict{"name":name, "wt":weight fraction %, "temp": initial temperature K, "h": enthalpy kJ/mol, "elem": element}
    eps: float,
        Area ratio of nozzle throat & exit, Ae/At
    list_omit: list of string, default is empty list
        chemical species list for omitting from calculation
    list_only: list of string, default is empty list
        list of manually assinglinged chemical species
    fname: string, optional, default is False
        file name of generated .inp file
    """
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    num_round = int(2) #the number of decimal places in "Pc" & "of"
    if fname:
        inp_fname = fname + ".inp"
    else:
        inp_fname = "Pc_{:0>5.2f}__of_{:0>5.2f}.inp".format(round(Pc,num_round), round(of,num_round)) #.inp file name, e.g. "Pc=1.00_of=6.00.inp"
    file = open(os.path.join(path,inp_fname), "w")

    Pc = Pc * 10    #Pc:Chamber pressure [bar]
    prob = "case={} o/f={} rocket {} tcest,k=3800 p,bar={} sup,ae/at={}".format(inp_fname, round(of,4), option, round(Pc,4), round(eps,4))
    oxid = ""
    for i in range(len(list_oxid)):
        if len(str(list_oxid[i]["h"]))==0:
            oxid = oxid + "\toxid={} wt={} t,k={} \n".format(list_oxid[i]["name"], list_oxid[i]["wt"], list_oxid[i]["temp"])
        else:
            oxid = oxid + "\toxid={} wt={} t,k={} h,kj/mol={} {} \n".format(list_oxid[i]["name"], list_oxid[i]["wt"], list_oxid[i]["temp"], list_oxid[i]["h"], list_oxid[i]["elem"])
    fuel = ""
    for i in range(len(list_fuel)):
        if len(str(list_fuel[i]["h"]))==0:
            fuel = fuel + "\tfuel={} wt={} t,k={} \n".format(list_fuel[i]["name"], list_fuel[i]["wt"], list_fuel[i]["temp"])
        else:
            fuel = fuel + "\tfuel={} wt={} t,k={} h,kj/mol={} {} \n".format(list_fuel[i]["name"], list_fuel[i]["wt"], list_fuel[i]["temp"], list_fuel[i]["h"], list_fuel[i]["elem"])
    optional = ""
    if len(list_omit) != 0:
        omit = "omit\n\t"
        for i in list_omit:
            omit += i + " "
        optional += omit + "\n"
    if len(list_only) != 0:
        only = "only\n\t"
        for i in list_only:
            only += i + " "
        optional += only + "\n"
#    outp = "siunits short"
    outp = "transport"
    file.write("prob\n\t{0}\nreact\n{1}{2}{3}output\t{4}\nend\n".format(prob,oxid,fuel,optional,outp))
    file.close()


def make_inp_name(path, option, list_species, Pc, eps, list_omit=[], list_only=[], fname=False):
    """
    Write information in input file, "*.inp".
    This mode should be used when exe program uses non-oxidize and non-fuel spieces.
    
    Parameter
    ---------
    path : string
        Path at which "*.inp" file is saved
    option: string
        Calculation option, wtheher using equilibrium composition or frozen composition.
    list_species: list of dictionary,
        The list has an information about chemical species as dict type; dict{"name": name, "wt": weight fraction %, "temp": initial temperature K, "h": enthalpy kJ/mol, "elem": element}
    Pc: float,
        Camberpressure, [MPa]
    eps: float,
        Area ratio of nozzle throat & exit, Ae/At
    list_omit: list of string, default is empty list
        chemical species list for omitting from calculation
    list_only: list of string, default is empty list
        list of manually assinglinged chemical species
    fname: string, optional, default is False
        file name of generated .inp file
    """

    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    num_round = int(2) #the number of decimal places in "Pc" & "of"
    if fname:
        inp_fname = fname + ".inp"
    else:
        inp_fname = "Pc={:0>5.2f}_".format(round(Pc,num_round))
        for dic in list_species:
            inp_fname = inp_fname + "{}={:0>5.1f}".format(dic["name"], round(dic["wt"],num_round))   
        inp_fname = inp_fname + ".inp"
    file = open(os.path.join(path,inp_fname), "w")

    Pc = Pc * 10    #Pc:Chamber pressure [bar]
    prob = "case={} rocket {} tcest,k=3800 p,bar={} sup,ae/at={}".format(inp_fname, option, round(Pc,4), round(eps,4))
    name = ""
    for i in range(len(list_species)):
        if len(str(list_species[i]["h"]))==0:
            name = name + "\tname={} wt={} t,k={} \n".format(list_species[i]["name"], list_species[i]["wt"], list_species[i]["temp"])
        else:
            name = name + "\tname={} wt={} t,k={} h,kj/mol={} {} \n".format(list_species[i]["name"], list_species[i]["wt"], list_species[i]["temp"], list_species[i]["h"], list_species[i]["elem"])
    optional = ""
    if len(list_omit) != 0:
        omit = "omit\n\t"
        for i in list_omit:
            omit += i + " "
        optional += omit + "\n"
    if len(list_only) != 0:
        only = "only\n\t"
        for i in list_only:
            only += i + " "
        optional += only + "\n"
#    outp = "siunits short"
    outp = "transport"
    file.write("prob\n\t{0}\nreact\n{1}{2}output\t{3}\nend\n".format(prob,name,optional,outp))
    file.close()


if __name__ == "__main__":
    myclass = Cui_input()
    myclass.gen_all()
