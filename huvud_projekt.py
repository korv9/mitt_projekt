import requests #hämta grejer från api
import os
from PIL import Image, ImageTk #för att visa bilden
from io import BytesIO #hantera bild data
import tkinter 
import random
import datetime
import threading


class GUI: #klass för tkinter GUI, 
    def __init__(self) -> None:
        self.root=tkinter.Tk()
        self.root.title("weather app")
        self.root.geometry("1500x1500")
        self.text_label=tkinter.Label(self.root,text="welcome to app")
        self.text_label.pack()
        
        self.bg_label = tkinter.Label(self.root) #backgrundsbild label
        self.bg_label.place(relwidth=1, relheight=1)
        
        # värden för att centrera labels o buttons
        window_width = 1500 
        label_width = 300 
        button_width = 160 
        entry_width = 160
        
        self.city_name = tkinter.StringVar() #sparar det man skriver i boxen 
        self.name_entry = tkinter.Entry(self.root,textvariable = self.city_name,  width=20, font=('calibre',10,'normal'))
        self.name_entry.place(x=(window_width - entry_width) //2 , y=800) #bakar in formeln window width - label_width / 2 för att få det centrerat

        label_width = 300 # värde för label pixel bredd, för att kunna centrera dom
        button_width = 160 # värde för button bredd
        #tomma labels för att sedan uppdatera senare
        self.weather_label = tkinter.Label(self.root, font=40, text="")
        self.weather_label.place(x=(window_width - label_width)//2, y=60)

        self.temperature_label = tkinter.Label(self.root, font= 40, text="")
        self.temperature_label.place(x=(window_width - label_width)//2, y=100)

        #self.image_label = tkinter.Label(self.root)
        #self.image_label.pack(pady=10)
        
        self.fetch_button = tkinter.Button(self.root, text="Get Weather",width=20, command=lambda: self.fetch_weather()) 
        self.fetch_button.place(x=(window_width - button_width)//2 - button_width, y=900)

        self.random_city_button = tkinter.Button(self.root, text="surprise city....",width=20, command=lambda: self.fetch_random_city_weather())
        self.random_city_button.place(x=(window_width - button_width)//2 + button_width, y=900)




# knapp som kallar på funktion



    def fetch_weather(self):
        city = City(self.city_name.get(),self)
        city.get_weather()
        city.get_picture()
        
    def fetch_random_city_weather(self): #funktion för att hämta random stad från lista
        cities_file_path = "stor_projekt\cities_list.txt"
        
        if os.path.exists(cities_file_path): #kollar om filen finns
            
            with open(cities_file_path, "r") as city_file:
                    cities = city_file.read().splitlines()
            
            if cities: #om listan inte är tom
                random_city = random.choice(cities) #väljer random stad
                city = City(random_city, self)
                city.get_weather() 
                city.get_picture()





class City: #klass för att strukturera upp väderdatan stad för stad
    def __init__(self,name, gui) -> None:
        self.name = name
        self.gui = gui
        
 
    def save_city(self): #funktion att spara städer för att sen randomizea 
        cities_file_path = "stor_projekt\cities_list.txt"
          
        if not os.path.exists(cities_file_path): #skapar fil om den inte finns
          open(cities_file_path, 'w').close()
          
          with open(cities_file_path, "r") as city_file: 
               cities = city_file.read().splitlines() # delar upp efter raderna
          
          if self.name not in cities: # för att kolla så att inte en stad redan är skriven 
                with open(cities_file_path, "a") as city_file:
                      city_file.write(f"{self.name}\n")
    
    
    


    
    
    def get_weather(self):# hämtar info och skriver ut väder
        
        url = f"http://api.weatherapi.com/v1/current.json?key={API_key_weather}&q={self.name}" # skickar in API nyckeln i url samt stadens namn

        try:
                response = requests.get(url).json()
                data = response
                
                if "error" in data: # det kan bli error trots statuscode 200, om den inte hittar angivna staden
                    GUI.weather_label.config(text="har aldrig hört talats om den där staden!") 
                else:
                   #skrivet ut värden om vädret från JSon api
                    temp = response["current"]["temp_c"]
                    weather = response["current"]["condition"]["text"]
                    
                    
                    self.latitude = response["location"]["lat"]
                    self.longitude = response["location"]["lon"]
                    self.country = response["location"]["country"]
                    
                    
                    
                    #skriver ut till textlabels
                    self.gui.temperature_label.config(text=f" {self.name}, {self.country} has a temperature of {temp}C", font = "30")
                    
                    self.gui.weather_label.config( text=f" It is {weather} in {self.name}!", font = "30", )
                    
    
        except Exception as e:
                
                print(f"nåt gick fel {e}")
    
     
    def get_picture(self):
         
         datum = datetime.date.today()
         # skickar in koordinaterna hämtade från Väder funktionen, samt datum och api key. 
         url_nasa = f"https://api.nasa.gov/planetary/earth/imagery?lon={self.longitude}&lat={self.latitude}&date={datum}&dim=0.09&api_key={API_key_nasa}" #&dim=0.3
         
         def fetch_image():
            try:
                response_nasa = requests.get(url_nasa)
                
                
                if response_nasa.status_code == 200: #IF sats för att se om API har hämtats rätt
                
                    
                    
                    # tar satellit bilden och öppnar bilden 
                    image = Image.open(BytesIO(response_nasa.content))
                    
                    image = image.resize((1500, 1500),)# Image.ANTIALIAS)  # minskar storleken på bilden
                    img_tk = ImageTk.PhotoImage(image) # konverterar bilden med photoimage så den kommer fram i tkinter

                    #tkinter label för bilden
                    
                    
                    self.gui.bg_label.config(image=img_tk)
                    self.gui.bg_label.image = img_tk
                    
                    
                    #lägger spar funktion i get_picture eftersom den krånglar mer med koordinater än get_weather
                    self.save_city()


                
                        
                else:
                    print("misslyckades att hämta bild")

            except Exception as e:
                
                print(f"nåt gick fel med bilden {e}")
         threading.Thread(target=fetch_image).start() #threadar funktionen så programmet inte hakar upp sig när bilden hämtas



with open("stor_projekt/api_key.txt","r") as API_file:   #öppnar API_key filen o läser de två nycklarna
             API_keys = API_file.readlines()
             API_keys = [key.strip() for key in API_keys]  # tar bort tomrum 
             API_key_weather = API_keys[0] # läser rad 1 som är API nyckeln till openweater
             API_key_nasa = API_keys[1] # läser rad 2 som är API nyckeln till nasa


if __name__ == "__main__":
    gui = GUI()

    gui.root.mainloop()
