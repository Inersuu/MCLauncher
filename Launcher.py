import tkinter as tk
import Vloader as vl
import Dfile as df
import Start as start

class Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minecraft Launcher")
        self.root.geometry("400x300")

        self.version_label = tk.Label(self.root, text="Выберите версию:")
        self.version_label.pack()

        self.version_var = tk.StringVar(self.root)
        self.version_var.set("1.12.2")  # По умолчанию
        vl.versions(self)
        '''
        a = ["1.19.2","1.18.2","1.17.1"]
        #self.version_menu = tk.OptionMenu(self.root, self.version_var, "1.19.2", "1.18.2", "1.17.1")
        self.version_menu = tk.OptionMenu(self.root, self.version_var, a[0])
        '''
        

        self.play_button = tk.Button(self.root, text="Загрузить", command=self.download_game_vession).place(relx=.5,rely=.5,anchor='s',width=70)
        #self.play_button.pack()
        self.play_button = tk.Button(text="Запуск", command=self.launch_games).place(relx=.9,rely=.95,anchor='s',width=70)
        #self.play_button = tk.Entry(text="Введите логин").place(relx=.5,rely=.95,anchor='s')
        self.entry = tk.Entry(self.root)
        self.entry.place(relx=.5,rely=.95,anchor='s')
        self.entry.delete(0, tk.END)  # Очищаем поле ввода
        self.entry.insert(0, "Введите логин")  # Вставляем сообщение

        self.label2 = tk.Label(self.root,text="MB")
        self.label2.place(relx=.7,rely=.14)
        self.entry2 = tk.Entry(self.root)
        self.entry2.place(relx=.7,rely=.2,width=100)
        self.entry2.insert(0, "2048")  # Вставляем сообщение
        #self.play_button.pack()

    '''
    def versions(self):
        manifest = vl.get_version_manifest()
        for version in manifest["versions"]:
            self.version_menu = tk.OptionMenu(self.root, self.version_var, version["id"])
            #print(version["id"])
    ''' 
    
    def launch_games(self):
        version = self.version_var.get()
        username = self.entry.get()  
        MB = self.entry2.get()
        
        if username and username != "Введите логин":  
            print(f"Запуск Minecraft {version} с логином {username}...")
            start.launch_game(version,username,MB)
        else:
            print("Ошибка: Введите логин!")
    
    def download_game_vession(self):
        print('test')
        a = self.version_var.get()

        df.download_version(a)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()