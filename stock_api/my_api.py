from flask import Flask, request, jsonify
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
import json
#C:\Users\riley\Desktop\robotics\Cyber\Personal Projects\Python\Selenium\filamentStock.py

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

filaments_json = open("filaments_dict.json")
filaments_file = json.load(filaments_json)

class Filament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.String(10), unique=False, nullable=False)
    colours = db.relationship("Colour", backref="filament", lazy=True)
    
    def __repr__(self):
        return f"{self.name}, {self.price}, {self.colours}"
    
class Colour(db.Model):
    colour_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    instock = db.Column(db.Boolean, nullable=False)
    filament_id = db.Column(db.Integer, db.ForeignKey("filament.id"), nullable=False)
    
    def __repr__(self):
        return f"{self.name}, {self.instock}"


#Routes

@app.route("/", methods=["GET"])
def index():
    filaments = Filament.query.all()
    output = []
    
    for filament in filaments:
        filament_data = {"id": filament.id, "name": filament.name, "price": filament.price}
        colours_data = []
        for colour in filament.colours:
            colours_data.append({"colour_id": colour.colour_id, "name": colour.name, "instock": colour.instock})
        filament_data["colours"] = colours_data
        output.append(filament_data)
    
    return jsonify({"filaments": output})


@app.route("/filament", methods=["GET"])
def get_filament_by_query():
    query = request.query_string.decode()
    param_pair = {}
    valid_filaments = Filament.query.all()
    params = []
    output = []
    data = {"filament": {}}
    
    if "=" not in query:
        for filament in valid_filaments:
            single_colours_data = []
            for colour in filament.colours:
                single_colours_data.append({"colour_id": colour.colour_id, "name": colour.name, "instock": colour.instock})
            single_param_data = {}
            single_param_data = {"id": filament.id, "name": filament.name, "price": filament.price, "colours": single_colours_data}
                
            output.append({query: single_param_data[query]})
            
    
    if "&" in query:
        for item in query.split("&"):
            if "=" in item:
                item = item.split("=")
                params.append(item)
    else:
        if "=" in query:
            new_query = query.split("=")
            params.append(new_query)

        
    for filament in valid_filaments:
        colours_data = []
        filament_data = {}
        filament_data = {"id": filament.id, "name": filament.name, "price": filament.price}
        
        for colour in filament.colours:
            colours_data.append({"colour_id": colour.colour_id, "name": colour.name, "instock": colour.instock})
            
        filament_data["colours"] = colours_data
        
        data["filament"][filament.name] = filament_data
        
    for key, value in params:
        if "%20" in value:
            value = value.replace("%20", " ")
        
        for item in data["filament"].keys():
            if str(data["filament"][item][key]) == str(value) and str(data["filament"][item][key]) not in output:
                output.append(data["filament"][item])
    
    return jsonify(output)


#Create tables when database needs updating
'''
with app.app_context():
    db.create_all()
    
    for key, value in filaments_file.items():
        name = key
        price = filaments_file[key]["price"]
        
        new_filament = Filament(name=name, price=price)
        db.session.add(new_filament)
        db.session.commit()
        
        for i in value["colours"]:
            name = i[0]
            if i[1] == "In stock":
                instock = True
            elif i[1] == "Out of stock":
                instock = False
            filament = new_filament
            
            new_filament_colour = Colour(name=name, instock=instock, filament=filament)

            db.session.add(new_filament_colour)
            db.session.commit()
'''


if __name__ == "__main__":
    app.run(debug=True)