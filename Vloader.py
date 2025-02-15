import requests
import tkinter as tk

def get_version_manifest():
    url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    response = requests.get(url)
    return response.json()
def getvm():
    manifest = get_version_manifest()
    for version in manifest["versions"]:
        print(version["id"])
def versions(self):
        vers = []
        manifest = get_version_manifest()
        ban = 'abcdefghijklmnopqrstuvwxyz'
        for version in manifest["versions"]:  
              
            vers.append(version["id"])
            
            #print(version["id"])
        res = []
        for sub in vers:
            flag = 0
            for ele in sub:
                if ele in ban:
                    flag = 1
            if not flag:
                res.append(sub)  
        self.version_menu = tk.OptionMenu(self.root, self.version_var, *res)
        self.version_menu.pack()
getvm()