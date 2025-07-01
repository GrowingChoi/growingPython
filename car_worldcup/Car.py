class Car:
    def __init__(self ,car_id:int = 0, model:str = "", fuel_type:str= "", car_level:str= "", outfit:str= "", 
                 horse_power:str= "", price:int = 0, fuel_effic:str= "", engine_type:str= "", img_url:str= ""):


        self.car_id =car_id
        self.model =model
        self.fuel_type = fuel_type
        self.car_level = car_level
        self.outfit = outfit
        self.horse_power = horse_power
        self.price = price
        self.fuel_effic = fuel_effic
        self.engine_type = engine_type
        self.img_url = img_url